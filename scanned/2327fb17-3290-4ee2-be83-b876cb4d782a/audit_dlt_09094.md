# [?] fix(core): handle stack overflow on stm32f4 properly

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-04-27
Source: https://github.com/trezor/trezor-firmware/commit/32fa8e164ab9afc6e6d170599846f025fa307efb
Type: security-commit

## Details
fix(core): handle stack overflow on stm32f4 properly

[no changelog]

Co-authored-by: Copilot <copilot@github.com>

## Patch
### core/embed/sys/task/stm32/systask.c
```diff
@@ -790,9 +790,9 @@ __attribute__((naked, no_stack_protector)) void MemManage_Handler(void) {
       "MOV      R1, LR                \n"  // R1 = EXC_RETURN code
 #if !(defined(__ARM_ARCH_8M_MAIN__) || defined(__ARM_ARCH_8M_BASE__))
       "TST      LR, #0x4              \n"  // Return stack (1=>PSP, 0=>MSP)
-      "BEQ      1f                    \n"  // Skip stack ptr checking for PSP
+      "BNE      1f                    \n"  // Skip stack ptr checking for PSP
       "LDR      R2, =%[sstack]        \n"
-      "CMP      R0, R2                \n"  // Check if PSP is below the stack
+      "CMP      R0, R2                \n"  // Check if MSP is below the stack
       "ITT      LO                    \n"  // base
       "LDRLO    R2, =%[estack]        \n"
       "MSRLO    MSP, R2               \n"  // Reset MSP
```
