# [?] fix(tests): do not trip deadlock detection in autolock test

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-09-19
Source: https://github.com/trezor/trezor-firmware/commit/73c8149528e94115471f24b07e31e9a02f71bd04
Type: security-commit

## Details
fix(tests): do not trip deadlock detection in autolock test

## Patch
### tests/click_tests/test_autolock.py
```diff
@@ -182,12 +182,17 @@ def sleepy_filter(msg: MessageType) -> MessageType:
     with device_handler.client:
         device_handler.client.set_filter(messages.TxAck, sleepy_filter)
         # confirm transaction
+        # In all cases we set wait=False to avoid waiting for the screen and triggering
+        # the layout deadlock detection. In reality there is no deadlock but the
+        # `sleepy_filter` delays the response by 10 secs while the layout deadlock
+        # timeout is 3. In this test we don't need the result of the input event so
+        # waiting for it is not necessary.
         if debug.layout_type is LayoutType.TT:
-            debug.click(buttons.OK)
+            debug.click(buttons.OK, wait=False)
         elif debug.layout_type is LayoutType.Mercury:
-            debug.click(buttons.TAP_TO_CONFIRM)
+            debug.click(buttons.TAP_TO_CONFIRM, wait=False)
         elif debug.layout_type is LayoutType.TR:
-            debug.press_middle()
+            debug.press_middle(wait=False)
 
         signatures, tx = device_handler.result()
         assert len(signatures) == 1
```
