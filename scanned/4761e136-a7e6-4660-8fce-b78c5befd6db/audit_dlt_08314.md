# [?] idl: Fix panicking on tests (#3197)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2024-08-25
Source: https://github.com/otter-sec/anchor/commit/04985802587c693091f836e0083e4412148c0ca6
Type: security-commit

## Details
idl: Fix panicking on tests (#3197)

## Patch
### CHANGELOG.md
```diff
@@ -60,6 +60,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 - lang: Fix compilation warnings due to unused deprecated program id macros ([#3170](https://github.com/coral-xyz/anchor/pull/3170)).
 - ts: Remove `crypto-hash` dependency ([#3171](https://github.com/coral-xyz/anchor/pull/3171)).
 - ts: Improve error message of unsupported `view` method ([#3177](https://github.com/coral-xyz/anchor/pull/3177)).
+- idl: Fix panicking on tests ([#3197](https://github.com/coral-xyz/anchor/pull/3197)).
 
 ### Breaking
 
```

### lang/syn/src/idl/defined.rs
```diff
@@ -497,9 +497,7 @@ pub fn gen_idl_type(
                 use quote::ToTokens;
 
                 let source_path = proc_macro2::Span::call_site().source_file().path();
-                let lib_path = find_path("lib.rs", &source_path).expect("lib.rs should exist");
-
-                if let Ok(ctx) = CrateContext::parse(lib_path) {
+                if let Ok(Ok(ctx)) = find_path("lib.rs", &source_path).map(CrateContext::parse) {
                     let name = path.path.segments.last().unwrap().ident.to_string();
                     let alias = ctx.type_aliases().find(|ty| ty.ident == name);
                     if let Some(alias) = alias {
```
