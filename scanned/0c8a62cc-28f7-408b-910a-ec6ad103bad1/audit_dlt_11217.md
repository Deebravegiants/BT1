# [?] fix panic handler

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2024-04-16
Source: https://github.com/a16z/jolt/commit/9042cec462fd5d7871d14ee00476607ef2314adb
Type: security-commit

## Details
fix panic handler

## Patch
### jolt-sdk/macros/src/lib.rs
```diff
@@ -48,6 +48,7 @@ impl MacroBuilder {
         let analyze_fn = self.make_analyze_function();
         let preprocess_fn = self.make_preprocess_func();
         let prove_fn = self.make_prove_func();
+        let panic_fn = self.make_panic();
 
         let main_fn = if let Some(func) = self.get_func_selector() {
             if self.get_func_name().to_string() == func {
@@ -66,6 +67,7 @@ impl MacroBuilder {
             #preprocess_fn
             #prove_fn
             #main_fn
+            #panic_fn
         }
         .into()
     }
@@ -327,6 +329,14 @@ impl MacroBuilder {
                 #handle_return
             }
 
+            // pub extern "C" fn jolt_panic() {
+            //     unsafe {
+            //         core::ptr::write_volatile(#panic_address as *mut u8, 1);
+            //     }
+
+            //     loop {}
+            // }
+
             // #[cfg(feature = "guest")]
             // #[panic_handler]
             // fn panic(_info: &PanicInfo) -> ! {
@@ -339,6 +349,24 @@ impl MacroBuilder {
         }
     }
 
+    fn make_panic(&self) -> TokenStream2 {
+        let attributes = self.parse_attributes();
+        let memory_layout =
+            MemoryLayout::new(attributes.max_input_size, attributes.max_output_size);
+
+        let panic_address = memory_layout.panic;
+        quote! {
+            #[no_mangle]
+            pub extern "C" fn jolt_panic() {
+                unsafe {
+                    core::ptr::write_volatile(#panic_address as *mut u8, 1);
+                }
+
+                loop {}
+            }
+        }
+    }
+
     fn make_imports(&self) -> TokenStream2 {
         quote! {
             #[cfg(not(feature = "guest"))]
```
