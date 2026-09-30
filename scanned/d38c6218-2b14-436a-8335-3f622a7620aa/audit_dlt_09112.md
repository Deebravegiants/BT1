# [?] fix(tests): fix click tests race condition

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-10-17
Source: https://github.com/trezor/trezor-firmware/commit/69770a42f472b852150e4d48858d2075a3814ca5
Type: security-commit

## Details
fix(tests): fix click tests race condition

## Patch
### core/src/trezor/ui/__init__.py
```diff
@@ -163,6 +163,7 @@ def __init__(self, layout: LayoutObj[T]) -> None:
         self.timers: dict[int, loop.Task] = {}
         self.result_box = loop.mailbox()
         self.button_request_box = loop.mailbox()
+        self.button_request_ack_pending: bool = False
         self.transition_out: AttachType | None = None
         self.backlight_level = BacklightLevels.NORMAL
         self.context: context.Context | None = None
@@ -281,26 +282,30 @@ def _event(self, event_call: Callable[..., LayoutState | None], *args: Any) -> N
         if __debug__ and CURRENT_LAYOUT is not self:
             raise wire.FirmwareError("layout received an event but it is not running")
 
+        first_paint = False
         state = event_call(*args)
         self.transition_out = self.layout.get_transition_out()
 
         if state is LayoutState.DONE:
             self._emit_message(self.layout.return_value())
 
         elif state is LayoutState.ATTACHED:
-            self._button_request()
-            if __debug__:
+            first_paint = True
+            self.button_request_ack_pending = self._button_request()
+            if self.button_request_ack_pending:
+                state = LayoutState.TRANSITIONING
+            elif __debug__:
                 self.notify_debuglink(self)
 
         if state is not None:
             self.state = state
 
-        if state is LayoutState.ATTACHED:
+        if first_paint:
             self._first_paint()
         else:
             self._paint()
 
-    def _button_request(self) -> None:
+    def _button_request(self) -> bool:
         """Process a button request coming out of the Rust layout."""
         if __debug__ and not self.button_request_box.is_empty():
             raise wire.FirmwareError(
@@ -310,13 +315,14 @@ def _button_request(self) -> None:
 
         res = self.layout.button_request()
         if res is None:
-            return
+            return False
 
         if self.context is None:
-            return
+            return False
 
         # in production, we don't want this to fail, hence replace=True
         self.button_request_box.put(res, replace=True)
+        return True
 
     def _paint(self) -> None:
         """Paint the layout and ensure that homescreen cache is properly invalidated."""
```
