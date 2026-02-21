package com.vanphuc.vaultitemlogger;

import com.terraformersmc.modmenu.api.ConfigScreenFactory;
import com.terraformersmc.modmenu.api.ModMenuApi;
import com.vanphuc.vaultitemlogger.config.ModConfig;

public class ModMenuIntegration implements ModMenuApi {
    @Override
    public ConfigScreenFactory<?> getModConfigScreenFactory() {

        return parent -> ModConfig.createConfigScreen(parent);
    }
}