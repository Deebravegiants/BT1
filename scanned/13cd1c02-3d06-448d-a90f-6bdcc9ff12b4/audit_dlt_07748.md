# [?] fix(compact): prevent bitflag overflow by using usize accumulator (#19408)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-10-31
Source: https://github.com/paradigmxyz/reth/commit/60fba66a4f7dea5232ba755a6ad713a6523ea88e
Type: security-commit

## Details
fix(compact): prevent bitflag overflow by using usize accumulator (#19408)

## Patch
### crates/storage/codecs/derive/src/compact/flags.rs
```diff
@@ -51,7 +51,7 @@ pub(crate) fn generate_flag_struct(
         quote! {
             buf.get_u8(),
         };
-        total_bytes.into()
+        total_bytes
     ];
 
     let docs = format!(
@@ -64,11 +64,11 @@ pub(crate) fn generate_flag_struct(
             impl<'a> #ident<'a> {
                 #[doc = #bitflag_encoded_bytes]
                 pub const fn bitflag_encoded_bytes() -> usize {
-                    #total_bytes as usize
+                    #total_bytes
                 }
                 #[doc = #bitflag_unused_bits]
                 pub const fn bitflag_unused_bits() -> usize {
-                    #unused_bits as usize
+                    #unused_bits
                 }
            }
         }
@@ -77,11 +77,11 @@ pub(crate) fn generate_flag_struct(
             impl #ident {
                 #[doc = #bitflag_encoded_bytes]
                 pub const fn bitflag_encoded_bytes() -> usize {
-                    #total_bytes as usize
+                    #total_bytes
                 }
                 #[doc = #bitflag_unused_bits]
                 pub const fn bitflag_unused_bits() -> usize {
-                    #unused_bits as usize
+                    #unused_bits
                 }
            }
         }
@@ -123,8 +123,8 @@ fn build_struct_field_flags(
     fields: Vec<&StructFieldDescriptor>,
     field_flags: &mut Vec<TokenStream2>,
     is_zstd: bool,
-) -> u8 {
-    let mut total_bits = 0;
+) -> usize {
+    let mut total_bits: usize = 0;
 
     // Find out the adequate bit size for the length of each field, if applicable.
     for field in fields {
@@ -138,7 +138,7 @@ fn build_struct_field_flags(
                 let name = format_ident!("{name}_len");
                 let bitsize = get_bit_size(ftype);
                 let bsize = format_ident!("B{bitsize}");
-                total_bits += bitsize;
+                total_bits += bitsize as usize;
 
                 field_flags.push(quote! {
                     pub #name: #bsize ,
@@ -170,7 +170,7 @@ fn build_struct_field_flags(
 /// skipped field.
 ///
 /// Returns the total number of bytes used by the flags struct and how many unused bits.
-fn pad_flag_struct(total_bits: u8, field_flags: &mut Vec<TokenStream2>) -> (u8, u8) {
+fn pad_flag_struct(total_bits: usize, field_flags: &mut Vec<TokenStream2>) -> (usize, usize) {
     let remaining = 8 - total_bits % 8;
     if remaining == 8 {
         (total_bits / 8, 0)
```

### crates/storage/codecs/derive/src/compact/mod.rs
```diff
@@ -238,11 +238,11 @@ mod tests {
             impl TestStruct {
                 #[doc = "Used bytes by [`TestStructFlags`]"]
                 pub const fn bitflag_encoded_bytes() -> usize {
-                    2u8 as usize
+                    2usize
                 }
                 #[doc = "Unused bits for new fields by [`TestStructFlags`]"]
                 pub const fn bitflag_unused_bits() -> usize {
-                    1u8 as usize
+                    1usize
                 }
             }
 
```
