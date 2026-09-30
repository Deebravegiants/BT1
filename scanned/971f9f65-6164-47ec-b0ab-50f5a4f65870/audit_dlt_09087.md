# [?] fix(core): fix overflowing text in Delizia bld

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-05-11
Source: https://github.com/trezor/trezor-firmware/commit/d48e3b24454b9c40f0d39393cf904c2a16934e58
Type: security-commit

## Details
fix(core): fix overflowing text in Delizia bld

- these should not be visible in the regular user flow anyway since we
introduced interactionless update

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_delizia/bootloader/mod.rs
```diff
@@ -209,11 +209,11 @@ impl BootloaderUI for UIDelizia {
         unwrap!(version_str.push_str(vendor));
 
         let title_str = if is_newinstall {
-            "INSTALL FIRMWARE"
+            "INSTALL FW"
         } else if is_newvendor {
             "CHANGE FW\nVENDOR"
         } else if version_cmp > 0 {
-            "UPDATE FIRMWARE"
+            "UPDATE FW"
         } else if version_cmp == 0 {
             "REINSTALL FW"
         } else {
```
