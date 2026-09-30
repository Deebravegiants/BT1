# [?] fix(core): fix device_menu crash on devices without a serial number

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-05-29
Source: https://github.com/trezor/trezor-firmware/commit/51790381e63e453bd01c06002240095a3fb8e496
Type: security-commit

## Details
fix(core): fix device_menu crash on devices without a serial number

[no changelog]

## Patch
### core/src/apps/homescreen/device_menu.py
```diff
@@ -117,7 +117,12 @@ async def handle_device_menu() -> None:
 
         firmware_type = "Bitcoin-only" if utils.BITCOIN_ONLY else "Universal"
         production_year = _get_production_year()
-        serial_no = utils.serial_number() if utils.USE_SERIAL_NUMBER else None
+
+        try:
+            serial_no = utils.serial_number() if utils.USE_SERIAL_NUMBER else None
+        except RuntimeError:
+            # Unprovisioned devices might not have a serial number
+            serial_no = "N/A"
 
         about_items: list[tuple[str | None, str | None, bool]] = [
             (TR.homescreen__firmware_version, firmware_version, False),
```
