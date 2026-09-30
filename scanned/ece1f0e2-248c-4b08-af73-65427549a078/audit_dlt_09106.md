# [?] fix(eckhart): allow device name to overflow

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-08-28
Source: https://github.com/trezor/trezor-firmware/commit/1cda8e659eb781a97dc7bcd4aac94d2c23ee495b
Type: security-commit

## Details
fix(eckhart): allow device name to overflow

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_eckhart/component/button.rs
```diff
@@ -104,6 +104,19 @@ impl Button {
             .with_radius(Self::MENU_ITEM_RADIUS)
     }
 
+    pub fn new_menu_item_with_overflowing_subtext(
+        text: TString<'static>,
+        stylesheet: ButtonStyleSheet,
+        subtext: TString<'static>,
+        subtext_style: &'static TextStyle,
+    ) -> Self {
+        Self::with_text_and_overflowing_subtext(text, subtext, subtext_style, None)
+            .with_text_align(Self::MENU_ITEM_ALIGNMENT)
+            .with_content_offset(Self::MENU_ITEM_CONTENT_OFFSET)
+            .styled(stylesheet)
+            .with_radius(Self::MENU_ITEM_RADIUS)
+    }
+
     #[cfg(feature = "micropython")]
     pub fn new_connection_item(
         text: TString<'static>,
@@ -155,6 +168,22 @@ impl Button {
             text,
             subtext,
             subtext_style,
+            subtext_overflow: false,
+            icon,
+        })
+    }
+
+    pub fn with_text_and_overflowing_subtext(
+        text: TString<'static>,
+        subtext: TString<'static>,
+        subtext_style: &'static TextStyle,
+        icon: Option<(Icon, Color)>,
+    ) -> Self {
+        Self::new(ButtonContent::TextAndSubtext {
+            text,
+            subtext,
+            subtext_style,
+            subtext_overflow: true,
             icon,
         })
     }
@@ -328,12 +357,7 @@ impl Button {
                 text.map(|t| self.text_height(t, *single_line, width))
             }
             ButtonContent::Icon(icon) => icon.toif.height(),
-            ButtonContent::TextAndSubtext {
-                text,
-                subtext: _,
-                subtext_style: _,
-                icon,
-            } => {
+            ButtonContent::TextAndSubtext { text, icon, .. } => {
                 let width = if icon.is_some() {
                     width - Self::CONN_ICON_WIDTH
                 } else {
@@ -464,6 +488,7 @@ impl Button {
                 text,
                 subtext,
                 subtext_style,
+                subtext_overflow,
                 icon,
             } => {
                 let text_baseline_height = self.baseline_text_height();
@@ -494,7 +519,9 @@ impl Button {
                 subtext.map(|subtext| {
                     #[cfg(feature = "ui_debug")]
                     {
-                        if subtext_style.text_font.text_width(subtext) > available_width {
+                        if subtext_style.text_font.text_width(subtext) > available_width
+                            && !subtext_overflow
+                        {
                             fatal_error!(&uformat!(len: 128, "Subtext too long: '{}'", subtext));
                         }
                     }
@@ -726,6 +753,7 @@ pub enum ButtonContent {
         text: TString<'static>,
         subtext: TString<'static>,
         subtext_style: &'static TextStyle,
+        subtext_overflow: bool,
         icon: Option<(Icon, Color)>,
     },
     Icon(Icon),
```

### core/embed/rust/src/ui/layout_eckhart/firmware/device_menu_screen.rs
```diff
@@ -97,6 +97,7 @@ pub enum DeviceMenuMsg {
 struct MenuItem {
     text: TString<'static>,
     subtext: Option<(TString<'static>, Option<&'static TextStyle>)>,
+    subtext_overflow: bool,
     stylesheet: &'static ButtonStyleSheet,
     connection_status: Option<bool>,
     action: Option<Action>,
@@ -111,6 +112,7 @@ impl MenuItem {
         Self {
             text,
             subtext: None,
+            subtext_overflow: false,
             stylesheet: MENU_ITEM_NORMAL,
             action,
             connection_status: None,
@@ -122,6 +124,16 @@ impl MenuItem {
         subtext: Option<(TString<'static>, Option<&'static TextStyle>)>,
     ) -> &mut Self {
         self.subtext = subtext;
+        self.subtext_overflow = false;
+        self
+    }
+
+    pub fn with_overflowing_subtext(
+        &mut self,
+        subtext: Option<(TString<'static>, Option<&'static TextStyle>)>,
+    ) -> &mut Self {
+        self.subtext = subtext;
+        self.subtext_overflow = true;
         self
     }
 
@@ -465,7 +477,7 @@ impl DeviceMenuScreen {
                 TR::words__name.into(),
                 Some(Action::Return(DeviceMenuMsg::DeviceName)),
             );
-            item_device_name.with_subtext(Some((device_name, None)));
+            item_device_name.with_overflowing_subtext(Some((device_name, None)));
             unwrap!(items.push(item_device_name));
         }
 
@@ -606,12 +618,21 @@ impl DeviceMenuScreen {
                     } else if let Some((subtext, subtext_style)) = item.subtext {
                         let subtext_style =
                             subtext_style.unwrap_or(&theme::TEXT_MENU_ITEM_SUBTITLE);
-                        Button::new_menu_item_with_subtext(
-                            item.text,
-                            *item.stylesheet,
-                            subtext,
-                            subtext_style,
-                        )
+                        if item.subtext_overflow {
+                            Button::new_menu_item_with_overflowing_subtext(
+                                item.text,
+                                *item.stylesheet,
+                                subtext,
+                                subtext_style,
+                            )
+                        } else {
+                            Button::new_menu_item_with_subtext(
+                                item.text,
+                                *item.stylesheet,
+                                subtext,
+                                subtext_style,
+                            )
+                        }
                     } else {
                         Button::new_menu_item(item.text, *item.stylesheet)
                     };
```
