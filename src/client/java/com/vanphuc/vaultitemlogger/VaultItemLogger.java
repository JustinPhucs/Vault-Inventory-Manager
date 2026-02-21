package com.vanphuc.vaultitemlogger;

import net.fabricmc.api.ModInitializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class VaultItemLogger implements ModInitializer {
    public static final String MOD_ID = "vault-item-logger";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    @Override
    public void onInitialize() {
        LOGGER.info("Vault Item Logger initialized!");
    }
}