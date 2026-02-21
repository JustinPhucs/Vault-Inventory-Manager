package com.vanphuc.vaultitemlogger.config;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import dev.isxander.yacl3.api.*;
import dev.isxander.yacl3.api.controller.IntegerSliderControllerBuilder;
import dev.isxander.yacl3.api.controller.StringControllerBuilder;
import dev.isxander.yacl3.api.controller.TickBoxControllerBuilder;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.text.Text;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;

public class ModConfig {
    private static final Path CONFIG_FILE = FabricLoader.getInstance().getConfigDir().resolve("vault-item-logger.json");
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static ModConfig INSTANCE = new ModConfig();

    public boolean enabled = true;
    public boolean showChatLogs = true;
    public String vaultTitleRegex = "Vaults? #(\\d+)";
    public int scanDelayMs = 500;

    public static ModConfig get() {
        return INSTANCE;
    }

    public void save() {
        try (FileWriter writer = new FileWriter(CONFIG_FILE.toFile())) {
            GSON.toJson(this, writer);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void load() {
        if (!CONFIG_FILE.toFile().exists()) {
            INSTANCE.save();
            return;
        }
        try (FileReader reader = new FileReader(CONFIG_FILE.toFile())) {
            INSTANCE = GSON.fromJson(reader, ModConfig.class);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static Screen createConfigScreen(Screen parent) {
        return YetAnotherConfigLib.createBuilder()
                .title(Text.literal("Vault Item Logger Settings"))
                .category(ConfigCategory.createBuilder()
                        .name(Text.literal("Cài đặt chung"))
                        .option(Option.<Boolean>createBuilder()
                                .name(Text.literal("Kích hoạt Mod"))
                                .binding(true, () -> get().enabled, val -> get().enabled = val)
                                .controller(TickBoxControllerBuilder::create)
                                .build())
                        .option(Option.<Boolean>createBuilder()
                                .name(Text.literal("Hiển thị Log trong Chat"))
                                .description(OptionDescription.of(Text.literal("Bật để thấy thông báo quét rương trong kênh chat nội bộ.")))
                                .binding(true, () -> get().showChatLogs, val -> get().showChatLogs = val)
                                .controller(TickBoxControllerBuilder::create)
                                .build())
                        .option(Option.<String>createBuilder()
                                .name(Text.literal("Tiêu đề Vault (Regex)"))
                                .binding("Vaults? #(\\d+)", () -> get().vaultTitleRegex, val -> get().vaultTitleRegex = val)
                                .controller(StringControllerBuilder::create)
                                .build())
                        .option(Option.<Integer>createBuilder()
                                .name(Text.literal("Delay quét (ms)"))
                                .binding(500, () -> get().scanDelayMs, val -> get().scanDelayMs = val)
                                .controller(opt -> IntegerSliderControllerBuilder.create(opt).range(0, 5000).step(100))
                                .build())
                        .group(OptionGroup.createBuilder()
                                .name(Text.literal("Tiện ích"))
                                .option(ButtonOption.createBuilder()
                                        .name(Text.literal("Copy đường dẫn Logs"))
                                        .action((screen, opt) -> {
                                            Path logPath = FabricLoader.getInstance().getGameDir().resolve("vault-logs");
                                            MinecraftClient.getInstance().keyboard.setClipboard(logPath.toAbsolutePath().toString());
                                            if (MinecraftClient.getInstance().player != null) {
                                                MinecraftClient.getInstance().player.sendMessage(Text.literal("§a[VaultLogger] Đã copy đường dẫn!"), true);
                                            }
                                        })
                                        .build())
                                .build())
                        .build())
                .save(get()::save)
                .build()
                .generateScreen(parent);
    }
}