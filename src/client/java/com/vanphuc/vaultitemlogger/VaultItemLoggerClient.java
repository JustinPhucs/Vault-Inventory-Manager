package com.vanphuc.vaultitemlogger;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.vanphuc.vaultitemlogger.config.ModConfig;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.screen.v1.ScreenEvents;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.screen.ingame.GenericContainerScreen;
import net.minecraft.inventory.Inventory;
import net.minecraft.item.ItemStack;
import net.minecraft.screen.GenericContainerScreenHandler;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledFuture;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class VaultItemLoggerClient implements ClientModInitializer {
	private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
	private static VaultItemLoggerClient INSTANCE;
	private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
	private ScheduledFuture<?> pendingTask;
	private String currentVaultId = null;

	@Override
	public void onInitializeClient() {
		INSTANCE = this;
		ModConfig.load();

		ScreenEvents.AFTER_INIT.register((client, screen, scaledWidth, scaledHeight) -> {
			if (!ModConfig.get().enabled) {
				currentVaultId = null;
				return;
			}

			if (screen instanceof GenericContainerScreen containerScreen) {
				String title = containerScreen.getTitle().getString();
				currentVaultId = extractVaultId(title);

				if (currentVaultId != null) {
					ChatUtils.debug("Đã khóa mục tiêu: Vault #" + currentVaultId);
					triggerScan(containerScreen);
				}
			} else {
				currentVaultId = null;
			}
		});
	}

	public static void triggerRealtimeScan() {
		MinecraftClient client = MinecraftClient.getInstance();
		if (INSTANCE != null && client.currentScreen instanceof GenericContainerScreen containerScreen) {
			if (INSTANCE.currentVaultId != null) {
				INSTANCE.triggerScan(containerScreen);
			}
		}
	}

	private void triggerScan(GenericContainerScreen screen) {
		if (pendingTask != null && !pendingTask.isDone()) {
			pendingTask.cancel(false);
		}

		pendingTask = scheduler.schedule(() -> scanAndLog(screen, currentVaultId),
				ModConfig.get().scanDelayMs, TimeUnit.MILLISECONDS);
	}

	private String extractVaultId(String title) {
		try {
			Pattern pattern = Pattern.compile(ModConfig.get().vaultTitleRegex, Pattern.CASE_INSENSITIVE);
			Matcher matcher = pattern.matcher(title);
			if (matcher.find()) {
				return matcher.groupCount() >= 1 ? matcher.group(1) : title.replaceAll("[^a-zA-Z0-9]", "_");
			}
		} catch (Exception e) {}
		return null;
	}

	public void scanAndLog(GenericContainerScreen screen, String vaultId) {
		GenericContainerScreenHandler handler = screen.getScreenHandler();
		Inventory inv = handler.getInventory();
		JsonArray itemsArray = new JsonArray();

		for (int i = 0; i < inv.size(); i++) {
			ItemStack stack = inv.getStack(i);
			if (!stack.isEmpty()) {
				JsonObject itemJson = new JsonObject();
				itemJson.addProperty("slot", i);
				itemJson.addProperty("id", stack.getItem().toString());
				itemJson.addProperty("count", stack.getCount());
				itemJson.addProperty("name", stack.getName().getString());
				itemsArray.add(itemJson);
			}
		}

		if (itemsArray.size() >= 0) {
			saveToFile(vaultId, itemsArray);
		}
	}

	private void saveToFile(String id, JsonArray data) {
		Path logDir = FabricLoader.getInstance().getGameDir().resolve("vault-logs");
		try {
			if (!Files.exists(logDir)) Files.createDirectories(logDir);
			Path filePath = logDir.resolve("vaults" + id + ".json");
			try (FileWriter writer = new FileWriter(filePath.toFile())) {
				GSON.toJson(data, writer);
				ChatUtils.info("§8[Real-time] §fĐã cập nhật Vault #" + id);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}