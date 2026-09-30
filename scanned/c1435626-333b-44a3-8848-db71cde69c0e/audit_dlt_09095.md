# [?] fix(python): avoid crash when scanning BLE multiple times

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-03-30
Source: https://github.com/trezor/trezor-firmware/commit/ca7efea8980982cd2563c165e37ffdd4a75829de
Type: security-commit

## Details
fix(python): avoid crash when scanning BLE multiple times

[no changelog]

## Patch
### python/src/trezorlib/transport/ble.py
```diff
@@ -194,7 +194,7 @@ def __init__(self, pipe: Connection) -> None:
         asyncio.run(self.main(pipe))
 
     async def main(self, pipe: Connection) -> None:
-        self.devices = {}
+        self.devices: dict[str, Peripheral] = {}
         self.did_scan = False
         LOG.debug("async BLE process started")
 
@@ -239,7 +239,7 @@ async def scan(self) -> list[tuple[str, str]]:
 
         # throw away non connected peripherals
         self.devices = {
-            addr: periph for addr, periph in self.devices.values() if periph.client
+            addr: periph for addr, periph in self.devices.items() if periph.client
         }
         for address, (dev, adv_data) in devices.items():
             if TREZOR_SERVICE_UUID not in adv_data.service_uuids:
@@ -254,7 +254,9 @@ async def scan(self) -> list[tuple[str, str]]:
                 self.devices[address] = Peripheral(dev, adv_data)
         self.did_scan = True
         return [
-            (periph.address, periph.device.name) for periph in self.devices.values()
+            (periph.address, periph.device.name)
+            for periph in self.devices.values()
+            if periph.device.name is not None
         ]
 
     async def connect(self, address: str) -> None:
@@ -263,7 +265,7 @@ async def connect(self, address: str) -> None:
 
         periph = self.devices.get(address)
         if not periph:
-            raise RuntimeError("device not found")
+            raise RuntimeError(f"Device not found: {address}")
 
         if periph.client:
             LOG.debug(f"Already connected to {periph.address}")
@@ -341,13 +343,17 @@ async def disconnect(self, address: str) -> None:
 
     async def read(self, address: str, timeout: float | None) -> bytes:
         periph = self.devices[address]
+        if periph.queue is None:
+            raise RuntimeError("Connect to peripheral before reading")
         try:
             return await asyncio.wait_for(periph.queue.get(), timeout=timeout)
-        except (TimeoutError, asyncio.TimeoutError):
-            raise Timeout(f"Timeout reading BLE packet ({timeout}s)")
+        except (TimeoutError, asyncio.TimeoutError) as err:
+            raise Timeout(f"Timeout reading BLE packet ({timeout}s)") from err
 
     async def write(self, address: str, chunk: bytes) -> None:
         periph = self.devices[address]
+        if periph.client is None:
+            raise RuntimeError("Connect to peripheral before writing")
         await periph.client.write_gatt_char(
             TREZOR_CHARACTERISTIC_RX, chunk, response=SHOULD_WRITE_WITH_RESPONSE
         )
```
