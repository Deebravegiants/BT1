# [?] device: protect against buffer overflow

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2026-09-19
Source: https://github.com/monero-project/monero/commit/f4626116b256c3fc669e4b594b0e83435c214f41
Type: security-commit

## Details
device: protect against buffer overflow

## Patch
### src/device/device_io_hid.cpp
```diff
@@ -219,6 +219,7 @@ namespace hw {
         if (result != 0) {
           break;
         }
+        ASSERT_X(offset + MAX_BLOCK <= sizeof(buffer), "HID response too large for buffer");
         hid_ret = hid_read_timeout(this->usb_device, buffer + offset, MAX_BLOCK, this->timeout);
         ASSERT_X(hid_ret>=0, "Unable to receive hidapi response. Error "+std::to_string(result)+": "+ safe_hid_error(this->usb_device));
         result = (unsigned int)hid_ret;
```
