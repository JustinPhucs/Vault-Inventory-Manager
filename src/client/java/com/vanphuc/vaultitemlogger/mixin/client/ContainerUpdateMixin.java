package com.vanphuc.vaultitemlogger.mixin.client;

import com.vanphuc.vaultitemlogger.VaultItemLoggerClient;
import net.minecraft.item.ItemStack;
import net.minecraft.screen.ScreenHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.List;

@Mixin(ScreenHandler.class)
public class ContainerUpdateMixin {

	@Inject(method = "updateSlotStacks", at = @At("TAIL"))
	private void onUpdateSlotStacks(int revision, List<ItemStack> stacks, ItemStack cursorStack, CallbackInfo ci) {
		VaultItemLoggerClient.triggerRealtimeScan();
	}

	@Inject(method = "setStackInSlot", at = @At("TAIL"))
	private void onSetStackInSlot(int slot, int revision, ItemStack stack, CallbackInfo ci) {
		VaultItemLoggerClient.triggerRealtimeScan();
	}
}