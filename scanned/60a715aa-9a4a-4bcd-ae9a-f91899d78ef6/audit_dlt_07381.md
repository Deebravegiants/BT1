# [?] fix(core): fix crash caused by marquee

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-11-12
Source: https://github.com/trezor/trezor-firmware/commit/30717bc5c46a743486bd79450a785a566b45e2ca
Type: security-commit

## Details
fix(core): fix crash caused by marquee

request_anim_frame will register a timer for RequestPaint, which will
then cause a crash. This commit fixes the crash, but makes the marquee
component not work.

[no changelog]

## Patch
### core/embed/rust/src/ui/model_tr/component/title.rs
```diff
@@ -99,6 +99,9 @@ impl Component for Title {
     fn event(&mut self, ctx: &mut EventCtx, event: Event) -> Option<Self::Msg> {
         if self.needs_marquee {
             if !self.marquee.is_animating() {
+                if matches!(Event::RequestPaint, _event) {
+                    return None;
+                }
                 self.marquee.start(ctx, Instant::now());
             }
             return self.marquee.event(ctx, event);
```
