package com.vanphuc.vaultitemlogger;

import com.vanphuc.vaultitemlogger.config.ModConfig;
import net.minecraft.client.MinecraftClient;
import net.minecraft.text.Text;

public class ChatUtils {
    private static final String PREFIX = "§b[VaultLogger] §f";

    public static void info(String message) {

        if (ModConfig.get().showChatLogs && MinecraftClient.getInstance().player != null) {
            MinecraftClient.getInstance().player.sendMessage(Text.literal(PREFIX + message), false);
        }
    }

    public static void debug(String message) {

        if (ModConfig.get().showChatLogs && MinecraftClient.getInstance().player != null) {
            MinecraftClient.getInstance().player.sendMessage(Text.literal("§7[Debug] " + message), false);
        }
    }
}