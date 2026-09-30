# [?] fix(eckhart): allow connection menu to overflow

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-08-29
Source: https://github.com/trezor/trezor-firmware/commit/ba06170d99d690e2a1db3e4103cf48291a3fd1e1
Type: security-commit

## Details
fix(eckhart): allow connection menu to overflow

[no changelog]

## Patch
### core/embed/rust/src/ui/layout_eckhart/component/button.rs
```diff
@@ -104,13 +104,13 @@ impl Button {
             .with_radius(Self::MENU_ITEM_RADIUS)
     }
 
-    pub fn new_menu_item_with_overflowing_subtext(
+    pub fn new_single_line_menu_item_with_overflowing_subtext(
         text: TString<'static>,
         stylesheet: ButtonStyleSheet,
         subtext: TString<'static>,
         subtext_style: &'static TextStyle,
     ) -> Self {
-        Self::with_text_and_overflowing_subtext(text, subtext, subtext_style, None)
+        Self::with_single_line_text_and_overflowing_subtext(text, subtext, subtext_style, None)
             .with_text_align(Self::MENU_ITEM_ALIGNMENT)
             .with_content_offset(Self::MENU_ITEM_CONTENT_OFFSET)
             .styled(stylesheet)
@@ -143,11 +143,16 @@ impl Button {
             }
         });
 
-        Self::with_text_and_subtext(text, subtext, subtext_style, Some(icon))
-            .with_text_align(Self::MENU_ITEM_ALIGNMENT)
-            .with_content_offset(Self::MENU_ITEM_CONTENT_OFFSET)
-            .styled(stylesheet)
-            .with_radius(Self::MENU_ITEM_RADIUS)
+        Self::with_single_line_text_and_overflowing_subtext(
+            text,
+            subtext,
+            subtext_style,
+            Some(icon),
+        )
+        .with_text_align(Self::MENU_ITEM_ALIGNMENT)
+        .with_content_offset(Self::MENU_ITEM_CONTENT_OFFSET)
+        .styled(stylesheet)
+        .with_radius(Self::MENU_ITEM_RADIUS)
     }
 
     pub const fn with_single_line_text(text: TString<'static>) -> Self {
@@ -164,28 +169,26 @@ impl Button {
         subtext_style: &'static TextStyle,
         icon: Option<(Icon, Color)>,
     ) -> Self {
-        Self::new(ButtonContent::TextAndSubtext {
+        Self::new(ButtonContent::text_and_subtext(
             text,
             subtext,
             subtext_style,
-            subtext_overflow: false,
             icon,
-        })
+        ))
     }
 
-    pub fn with_text_and_overflowing_subtext(
+    pub fn with_single_line_text_and_overflowing_subtext(
         text: TString<'static>,
         subtext: TString<'static>,
         subtext_style: &'static TextStyle,
         icon: Option<(Icon, Color)>,
     ) -> Self {
-        Self::new(ButtonContent::TextAndSubtext {
+        Self::new(ButtonContent::single_line_text_and_overflowing_subtext(
             text,
             subtext,
             subtext_style,
-            subtext_overflow: true,
             icon,
-        })
+        ))
     }
 
     pub const fn with_icon(icon: Icon) -> Self {
@@ -357,13 +360,20 @@ impl Button {
                 text.map(|t| self.text_height(t, *single_line, width))
             }
             ButtonContent::Icon(icon) => icon.toif.height(),
-            ButtonContent::TextAndSubtext { text, icon, .. } => {
+            ButtonContent::TextAndSubtext {
+                text,
+                single_line,
+                icon,
+                ..
+            } => {
                 let width = if icon.is_some() {
                     width - Self::CONN_ICON_WIDTH
                 } else {
                     width
                 };
-                text.map(|t| self.text_height(t, false, width) + self.baseline_subtext_height())
+                text.map(|t| {
+                    self.text_height(t, *single_line, width) + self.baseline_subtext_height()
+                })
             }
             #[cfg(feature = "micropython")]
             ButtonContent::HomeBar(..) => theme::ACTION_BAR_HEIGHT,
@@ -486,6 +496,7 @@ impl Button {
             }
             ButtonContent::TextAndSubtext {
                 text,
+                single_line,
                 subtext,
                 subtext_style,
                 subtext_overflow,
@@ -496,23 +507,33 @@ impl Button {
                     - 2 * self.content_offset.x
                     - icon.map_or(0, |_| Self::CONN_ICON_WIDTH);
                 let single_line_text = text.map(|t| {
-                    let (t1, t2) = split_two_lines(t, stylesheet.font, available_width);
-                    if t1.is_empty() || t2.is_empty() {
+                    if *single_line {
                         show_text(
                             t,
                             render_origin(text_baseline_height / 2 - constant::LINE_SPACE * 2),
                         );
                         true
                     } else {
-                        show_text(
-                            t1,
-                            render_origin(-(text_baseline_height / 2 + constant::LINE_SPACE * 3)),
-                        );
-                        show_text(
-                            t2,
-                            render_origin(text_baseline_height - constant::LINE_SPACE * 2),
-                        );
-                        false
+                        let (t1, t2) = split_two_lines(t, stylesheet.font, available_width);
+                        if t1.is_empty() || t2.is_empty() {
+                            show_text(
+                                t,
+                                render_origin(text_baseline_height / 2 - constant::LINE_SPACE * 2),
+                            );
+                            true
+                        } else {
+                            show_text(
+                                t1,
+                                render_origin(
+                                    -(text_baseline_height / 2 + constant::LINE_SPACE * 3),
+                                ),
+                            );
+                            show_text(
+                                t2,
+                                render_origin(text_baseline_height - constant::LINE_SPACE * 2),
+                            );
+                            false
+                        }
                     }
                 });
 
@@ -751,6 +772,7 @@ pub enum ButtonContent {
     },
     TextAndSubtext {
         text: TString<'static>,
+        single_line: bool,
         subtext: TString<'static>,
         subtext_style: &'static TextStyle,
         subtext_overflow: bool,
@@ -775,6 +797,38 @@ impl ButtonContent {
             single_line: true,
         }
     }
+
+    pub const fn text_and_subtext(
+        text: TString<'static>,
+        subtext: TString<'static>,
+        subtext_style: &'static TextStyle,
+        icon: Option<(Icon, Color)>,
+    ) -> Self {
+        Self::TextAndSubtext {
+            text,
+            single_line: false,
+            subtext,
+            subtext_style,
+            subtext_overflow: false,
+            icon,
+        }
+    }
+
+    pub const fn single_line_text_and_overflowing_subtext(
+        text: TString<'static>,
+        subtext: TString<'static>,
+        subtext_style: &'static TextStyle,
+        icon: Option<(Icon, Color)>,
+    ) -> Self {
+        Self::TextAndSubtext {
+            text,
+            single_line: true,
+            subtext,
+            subtext_style,
+            subtext_overflow: true,
+            icon,
+        }
+    }
 }
 
 #[derive(PartialEq, Eq, Clone, Copy)]
```

### core/embed/rust/src/ui/layout_eckhart/firmware/device_menu_screen.rs
```diff
@@ -97,7 +97,7 @@ pub enum DeviceMenuMsg {
 struct MenuItem {
     text: TString<'static>,
     subtext: Option<(TString<'static>, Option<&'static TextStyle>)>,
-    subtext_overflow: bool,
+    allow_overflow: bool,
     stylesheet: &'static ButtonStyleSheet,
     connection_status: Option<bool>,
     action: Option<Action>,
@@ -112,7 +112,7 @@ impl MenuItem {
         Self {
             text,
             subtext: None,
-            subtext_overflow: false,
+            allow_overflow: false,
             stylesheet: MENU_ITEM_NORMAL,
             action,
             connection_status: None,
@@ -124,16 +124,12 @@ impl MenuItem {
         subtext: Option<(TString<'static>, Option<&'static TextStyle>)>,
     ) -> &mut Self {
         self.subtext = subtext;
-        self.subtext_overflow = false;
+        self.allow_overflow = false;
         self
     }
 
-    pub fn with_overflowing_subtext(
-        &mut self,
-        subtext: Option<(TString<'static>, Option<&'static TextStyle>)>,
-    ) -> &mut Self {
-        self.subtext = subtext;
-        self.subtext_overflow = true;
+    pub fn allow_overflow(&mut self) -> &mut Self {
+        self.allow_overflow = true;
         self
     }
 
@@ -477,7 +473,9 @@ impl DeviceMenuScreen {
                 TR::words__name.into(),
                 Some(Action::Return(DeviceMenuMsg::DeviceName)),
             );
-            item_device_name.with_overflowing_subtext(Some((device_name, None)));
+            item_device_name
+                .with_subtext(Some((device_name, None)))
+                .allow_overflow();
             unwrap!(items.push(item_device_name));
         }
 
@@ -618,21 +616,12 @@ impl DeviceMenuScreen {
                     } else if let Some((subtext, subtext_style)) = item.subtext {
                         let subtext_style =
                             subtext_style.unwrap_or(&theme::TEXT_MENU_ITEM_SUBTITLE);
-                        if item.subtext_overflow {
-                            Button::new_menu_item_with_overflowing_subtext(
-                                item.text,
-                                *item.stylesheet,
-                                subtext,
-                                subtext_style,
-                            )
+                        let ctor = if item.allow_overflow {
+                            Button::new_single_line_menu_item_with_overflowing_subtext
                         } else {
-                            Button::new_menu_item_with_subtext(
-                                item.text,
-                                *item.stylesheet,
-                                subtext,
-                                subtext_style,
-                            )
-                        }
+                            Button::new_menu_item_with_subtext
+                        };
+                        ctor(item.text, *item.stylesheet, subtext, subtext_style)
                     } else {
                         Button::new_menu_item(item.text, *item.stylesheet)
                     };
```
