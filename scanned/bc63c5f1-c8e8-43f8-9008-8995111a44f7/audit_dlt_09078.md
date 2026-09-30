# [?] fix(core/rust): adjust menu item limits to prevent overflow errors

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-09-01
Source: https://github.com/trezor/trezor-firmware/commit/c81e063ea83f41dd82d018ce6fe7e6851e22a624
Type: security-commit

## Details
fix(core/rust): adjust menu item limits to prevent overflow errors

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_delizia/component/vertical_menu.rs
```diff
@@ -314,7 +314,15 @@ impl crate::trace::Trace for VerticalMenu {
     }
 }
 
-pub type VerticalMenuItems = Vec<VerticalMenuItem, 6>;
+pub const VERTICAL_MENU_ITEMS: usize = 6;
+
+/// `select_menu()` builds these out of a list already bounded by
+/// `MAX_MENU_ITEMS`, pushing with `unwrap!`, which panics on overflow rather
+/// than returning an error. Keep the capacity at or above that bound so raising
+/// `MAX_MENU_ITEMS` alone cannot turn a rejected menu into a fatal error.
+const _: () = assert!(VERTICAL_MENU_ITEMS >= crate::ui::ui_firmware::MAX_MENU_ITEMS);
+
+pub type VerticalMenuItems = Vec<VerticalMenuItem, VERTICAL_MENU_ITEMS>;
 
 pub enum VerticalMenuItem {
     Item(TString<'static>),
```

### core/embed/rust/src/ui/layout_eckhart/firmware/vertical_menu.rs
```diff
@@ -15,7 +15,13 @@ use crate::ui::util::animation_disabled;
 /// Presently, VerticalMenu holds only fixed number of buttons.
 pub const LONG_MENU_ITEMS: usize = 100;
 pub const MEDIUM_MENU_ITEMS: usize = 10;
-pub const SHORT_MENU_ITEMS: usize = 5;
+pub const SHORT_MENU_ITEMS: usize = 6;
+
+/// `select_menu()` builds a `ShortMenuVec` out of a list already bounded by
+/// `MAX_MENU_ITEMS`, and `MenuItems::push` panics on overflow rather than
+/// returning an error. Keep the capacity at or above that bound so raising
+/// `MAX_MENU_ITEMS` alone cannot turn a rejected menu into a fatal error.
+const _: () = assert!(SHORT_MENU_ITEMS >= crate::ui::ui_firmware::MAX_MENU_ITEMS);
 
 pub type LongMenuGc = GcBox<Vec<Button, LONG_MENU_ITEMS>>;
 pub type ShortMenuVec = Vec<Button, SHORT_MENU_ITEMS>;
```

### core/embed/rust/src/ui/ui_firmware.rs
```diff
@@ -15,7 +15,7 @@ use crate::ui::notification::Notification;
 pub const MAX_CHECKLIST_ITEMS: usize = 3;
 pub const MAX_WORD_QUIZ_ITEMS: usize = 3;
 pub const MAX_GROUP_SHARE_LINES: usize = 4;
-pub const MAX_MENU_ITEMS: usize = 5;
+pub const MAX_MENU_ITEMS: usize = 6;
 
 pub const MAX_PAIRED_DEVICES: usize = 8; // Maximum number of paired devices in the device menu
 
```
