# [?] fix(core/debug): make sure return_layout_change does not crash on a race condition

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-08-05
Source: https://github.com/trezor/trezor-firmware/commit/c39ba83c8b307e4b41ad3d99fa04c3129f5dae91
Type: security-commit

## Details
fix(core/debug): make sure return_layout_change does not crash on a race condition

[no changelog]

## Patch
### core/src/apps/debug/__init__.py
```diff
@@ -127,10 +127,13 @@ async def get_layout_change_content() -> list[str]:
 
         return content
 
-    async def return_layout_change() -> None:
+    async def return_layout_change() -> None:  # type: ignore [Return type of async generator]
         content_tokens = await get_layout_change_content()
 
-        assert isinstance(DEBUG_CONTEXT, context.Context)
+        # spin for a bit until DEBUG_CONTEXT becomes available
+        while not isinstance(DEBUG_CONTEXT, context.Context):
+            yield  # type: ignore [Return type of async generator]
+
         if storage.layout_watcher is LAYOUT_WATCHER_LAYOUT:
             await DEBUG_CONTEXT.write(DebugLinkLayout(tokens=content_tokens))
         else:
```
