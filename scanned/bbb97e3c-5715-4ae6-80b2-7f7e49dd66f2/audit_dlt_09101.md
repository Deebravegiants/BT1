# [?] fix(core): avoid integer underflow in `VerticalMenu::place`

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-10-22
Source: https://github.com/trezor/trezor-firmware/commit/fe21ddc727b6e79fcaa17c973a1bda83898e59d1
Type: security-commit

## Details
fix(core): avoid integer underflow in `VerticalMenu::place`

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_delizia/component/vertical_menu.rs
```diff
@@ -228,15 +228,14 @@ impl Component for VerticalMenu {
         self.n_items = n_items as usize;
 
         let mut remaining = bounds;
-        let n_seps = self.buttons.len() - 1;
         for (i, button) in self.buttons.iter_mut().take(self.n_items).enumerate() {
-            let (area_button, new_remaining) = remaining.split_top(MENU_BUTTON_HEIGHT);
-            button.place(area_button);
-            remaining = new_remaining;
-            if i < n_seps {
+            if i > 0 {
                 let (_area_sep, new_remaining) = remaining.split_top(MENU_SEP_HEIGHT);
                 remaining = new_remaining;
             }
+            let (area_button, new_remaining) = remaining.split_top(MENU_BUTTON_HEIGHT);
+            button.place(area_button);
+            remaining = new_remaining;
         }
         bounds
     }
```
