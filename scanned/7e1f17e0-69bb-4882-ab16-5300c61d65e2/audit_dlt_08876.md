# [?] Fixed derive of PanicDestruct (#3594)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-07-05
Source: https://github.com/starkware-libs/cairo/commit/336893775741f10c55fe22d5cd9f7937333df58e
Type: security-commit

## Details
Fixed derive of PanicDestruct (#3594)

## Patch
### crates/cairo-lang-plugins/src/plugins/derive.rs
```diff
@@ -290,7 +290,7 @@ fn get_panic_destruct_impl(name: &str, extra_info: &ExtraInfo) -> String {
         ExtraInfo::Struct { members, type_generics, other_generics } => {
             formatdoc! {"
                     impl {name}PanicDestruct{generics_impl} of PanicDestruct::<{name}{generics}> {{
-                        fn destruct(self: {name}{generics}, ref panic: Panic) nopanic {{
+                        fn panic_destruct(self: {name}{generics}, ref panic: Panic) nopanic {{
                             {}
                         }}
                     }}
```

### crates/cairo-lang-plugins/src/test_data/derive
```diff
@@ -75,7 +75,7 @@ impl TwoMemberStructDestruct<> of Destruct::<TwoMemberStruct<>> {
     }
 }
 impl TwoMemberStructPanicDestruct<> of PanicDestruct::<TwoMemberStruct<>> {
-    fn destruct(self: TwoMemberStruct<>, ref panic: Panic) nopanic {
+    fn panic_destruct(self: TwoMemberStruct<>, ref panic: Panic) nopanic {
         traits::PanicDestruct::panic_destruct(self.a, ref panic);
         traits::PanicDestruct::panic_destruct(self.b, ref panic);
     }
@@ -118,7 +118,7 @@ impl GenericStructDestruct<T, impl TDestruct: Destruct<T>> of Destruct::<Generic
     }
 }
 impl GenericStructPanicDestruct<T, impl TPanicDestruct: PanicDestruct<T>> of PanicDestruct::<GenericStruct<T, >> {
-    fn destruct(self: GenericStruct<T, >, ref panic: Panic) nopanic {
+    fn panic_destruct(self: GenericStruct<T, >, ref panic: Panic) nopanic {
         traits::PanicDestruct::panic_destruct(self.a, ref panic);
     }
 }
```
