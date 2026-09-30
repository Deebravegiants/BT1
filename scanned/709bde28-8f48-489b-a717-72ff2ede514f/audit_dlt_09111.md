# [?] fix(core): resolve crashes when running without display or with uninitialized display

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2024-12-10
Source: https://github.com/trezor/trezor-firmware/commit/0d3407b075ecca52dfcae31ab516a5100455b57f
Type: security-commit

## Details
fix(core): resolve crashes when running without display or with uninitialized display

[no changelog]

## Patch
### core/embed/rust/src/trezorhal/display.rs
```diff
@@ -55,20 +55,24 @@ pub fn refresh() {
 }
 
 #[cfg(feature = "framebuffer")]
-pub fn get_frame_buffer() -> (&'static mut [u8], usize) {
+pub fn get_frame_buffer() -> Option<(&'static mut [u8], usize)> {
     let mut fb_info = ffi::display_fb_info_t {
         ptr: ptr::null_mut(),
         stride: 0,
     };
 
     unsafe { ffi::display_get_frame_buffer(&mut fb_info) };
 
+    if fb_info.ptr.is_null() {
+        return None;
+    }
+
     let fb = unsafe {
         core::slice::from_raw_parts_mut(
             fb_info.ptr as *mut u8,
             DISPLAY_RESY as usize * fb_info.stride,
         )
     };
 
-    (fb, fb_info.stride)
+    Some((fb, fb_info.stride))
 }
```

### core/embed/rust/src/ui/shape/display/fb_mono8.rs
```diff
@@ -39,7 +39,13 @@ where
 
         let cache = DrawingCache::new(bump, bump);
 
-        let (fb, fb_stride) = display::get_frame_buffer();
+        let fb_info = display::get_frame_buffer();
+
+        if fb_info.is_none() {
+            return;
+        }
+
+        let (fb, fb_stride) = fb_info.unwrap();
 
         let mut canvas = unwrap!(Mono8Canvas::new(
             Offset::new(width, height),
```

### core/embed/rust/src/ui/shape/display/fb_rgb565.rs
```diff
@@ -32,7 +32,13 @@ where
 
         let cache = DrawingCache::new(bump_a, bump_b);
 
-        let (fb, fb_stride) = display::get_frame_buffer();
+        let fb_info = display::get_frame_buffer();
+
+        if fb_info.is_none() {
+            return;
+        }
+
+        let (fb, fb_stride) = fb_info.unwrap();
 
         let mut canvas = unwrap!(Rgb565Canvas::new(
             Offset::new(width, height),
```

### core/embed/rust/src/ui/shape/display/fb_rgba8888.rs
```diff
@@ -32,7 +32,13 @@ where
 
         let cache = DrawingCache::new(bump_a, bump_b);
 
-        let (fb, fb_stride) = display::get_frame_buffer();
+        let fb_info = display::get_frame_buffer();
+
+        if fb_info.is_none() {
+            return;
+        }
+
+        let (fb, fb_stride) = fb_info.unwrap();
 
         let mut canvas = unwrap!(Rgba8888Canvas::new(
             Offset::new(width, height),
```
