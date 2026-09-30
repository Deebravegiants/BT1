# [?] fix: replacing panic, unwrap & unimplemented error outs with `syn::Error` (#4291)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2026-04-13
Source: https://github.com/otter-sec/anchor/commit/c5d61328496ba9371bdf8faf6fae6990778a4773
Type: security-commit

## Details
fix: replacing panic, unwrap & unimplemented error outs with `syn::Error` (#4291)

## Patch
### lang/attribute/access-control/Cargo.toml
```diff
@@ -11,6 +11,13 @@ edition = "2021"
 [lib]
 proc-macro = true
 
+[lints.clippy]
+unwrap-used = "deny"
+expect-used = "deny"
+panic = "deny"
+unimplemented = "deny"
+indexing-slicing = "deny"
+
 [dependencies]
 proc-macro2 = "1"
 quote = "1"
```

### lang/attribute/access-control/src/lib.rs
```diff
@@ -56,8 +56,17 @@ pub fn access_control(
         .filter(|ac| !ac.is_empty())
         .map(|ac| format!("{ac})")) // Put back on the split char.
         .map(|ac| format!("{ac}?;")) // Add `?;` syntax.
-        .map(|ac| ac.parse().unwrap())
-        .collect();
+        .map(|ac| {
+            ac.parse::<proc_macro2::TokenStream>().map_err(|_| {
+                syn::Error::new(
+                    proc_macro2::Span::call_site(),
+                    format!("`#[access_control]` argument `{ac} is not valid Rust syntax"),
+                )
+                .into_compile_error()
+            })
+        })
+        .collect::<Result<Vec<_>, _>>()
+        .unwrap_or_else(|err| vec![err]);
 
     let item_fn = parse_macro_input!(input as syn::ItemFn);
 
```

### lang/attribute/account/Cargo.toml
```diff
@@ -11,6 +11,13 @@ edition = "2021"
 [lib]
 proc-macro = true
 
+[lints.clippy]
+unwrap-used = "deny"
+expect-used = "deny"
+panic = "deny"
+unimplemented = "deny"
+indexing-slicing = "deny"
+
 [features]
 anchor-debug = ["anchor-syn/anchor-debug"]
 idl-build = ["anchor-syn/idl-build"]
```

### lang/attribute/account/src/lazy.rs
```diff
@@ -43,6 +43,10 @@ pub fn gen_lazy(strct: &syn::ItemStruct) -> syn::Result<TokenStream> {
             let offset_of_ident = to_private_ident(format!("offset_of_{field_ident}"));
             let size_of_ident = to_private_ident(format!("size_of_{field_ident}"));
 
+            #[allow(
+                clippy::unwrap_used,
+                reason = "field i-1 always exists when iterating field i"
+            )]
             let offset = i.eq(&0).then(|| quote!(#disc_len)).unwrap_or_else(|| {
                 // Current offset is the previous field's offset + size
                 strct
```

### lang/attribute/account/src/lib.rs
```diff
@@ -356,7 +356,14 @@ pub fn derive_zero_copy_accessor(item: proc_macro::TokenStream) -> proc_macro::T
 
     let fields = match &account_strct.fields {
         syn::Fields::Named(n) => n,
-        _ => panic!("Fields must be named"),
+        _ => {
+            return syn::Error::new_spanned(
+                &account_strct.ident,
+                "#[derive(ZeroCopyAccessor)] requires a struct with named fields",
+            )
+            .into_compile_error()
+            .into()
+        }
     };
     let methods: Vec<proc_macro2::TokenStream> = fields
         .named
@@ -368,19 +375,53 @@ pub fn derive_zero_copy_accessor(item: proc_macro::TokenStream) -> proc_macro::T
                 .find(|attr| anchor_syn::parser::tts_to_string(&attr.path) == "accessor")
                 .map(|attr| {
                     let mut tts = attr.tokens.clone().into_iter();
-                    let g_stream = match tts.next().expect("Must have a token group") {
-                        proc_macro2::TokenTree::Group(g) => g.stream(),
-                        _ => panic!("Invalid syntax"),
+                    // if user writes #[accessor] with no arguments on a field, tts.next() returns None
+                    let g_stream = match tts.next() {
+                        Some(proc_macro2::TokenTree::Group(g)) => g.stream(),
+                        Some(_) => {
+                            return syn::Error::new_spanned(
+                                &attr.tokens,
+                                "invalid `#[accessor]` syntax, expected `#[accessor(Type)]`",
+                            )
+                            .into_compile_error();
+                        }
+                        None => {
+                            return syn::Error::new_spanned(
+                                &attr.tokens,
+                                "`#[accessor]` requires a type argument, e.g `#[accessor(MyType)]`",
+                            )
+                            .into_compile_error();
+                        }
                     };
                     let accessor_ty = match g_stream.into_iter().next() {
                         Some(token) => token,
-                        _ => panic!("Missing accessor type"),
+                        None => {
+                            return syn::Error::new_spanned(
+                                &attr.tokens,
+                                "`#[accessor]` requires a type inside the parantheses e.g \
+                                 `#[accessor(MyType)]`",
+                            )
+                            .into_compile_error()
+                        }
                     };
 
+                    #[allow(
+                        clippy::unwrap_used,
+                        reason = "accessor fields always have idents (named struct fields)"
+                    )]
                     let field_name = field.ident.as_ref().unwrap();
-
+                    #[allow(
+                        clippy::unwrap_used,
+                        reason = "get_<field_name> formed from a valid Rust identifier is always \
+                                  valid TokenStream"
+                    )]
                     let get_field: proc_macro2::TokenStream =
                         format!("get_{field_name}").parse().unwrap();
+                    #[allow(
+                        clippy::unwrap_used,
+                        reason = "set_<field_name> formed from a valid Rust identifier is always \
+                                  valid TokenStream"
+                    )]
                     let set_field: proc_macro2::TokenStream =
                         format!("set_{field_name}").parse().unwrap();
 
@@ -434,12 +475,21 @@ pub fn zero_copy(
                     // ```
                     is_unsafe = true;
                 } else {
-                    // TODO: how to return a compile error with a span (can't return prase error because expected type TokenStream)
-                    panic!("expected single ident `unsafe`");
+                    return syn::Error::new(
+                        proc_macro2::Span::from(ident.span()),
+                        "expected `unsafe`, e.g `#[zero_copy(unsafe)]`",
+                    )
+                    .into_compile_error()
+                    .into();
                 }
             }
             _ => {
-                panic!("expected single ident `unsafe`");
+                return syn::Error::new(
+                    proc_macro2::Span::from(arg.span()),
+                    "expected `unsafe`, e.g `#[zero_copy(unsafe)]`",
+                )
+                .into_compile_error()
+                .into();
             }
         }
     }
@@ -508,11 +558,11 @@ pub fn zero_copy(
         } else {
             quote! {}
         };
-        let zc_struct = syn::parse2(quote! {
+
+        let zc_struct = syn::parse_quote! {
             #derive_unsafe
             #ret
-        })
-        .unwrap();
+        };
         let idl_build_impl = anchor_syn::idl::impl_idl_build_struct(&zc_struct);
         return proc_macro::TokenStream::from(quote! {
             #ret
```

### lang/attribute/constant/Cargo.toml
```diff
@@ -11,6 +11,13 @@ edition = "2021"
 [lib]
 proc-macro = true
 
+[lints.clippy]
+unwrap-used = "deny"
+expect-used = "deny"
+panic = "deny"
+unimplemented = "deny"
+indexing-slicing = "deny"
+
 [features]
 anchor-debug = ["anchor-syn/anchor-debug"]
 idl-build = ["anchor-syn/idl-build"]
```

### lang/attribute/constant/src/lib.rs
```diff
@@ -11,6 +11,10 @@ pub fn constant(
     {
         use quote::quote;
 
+        #[allow(
+            clippy::unwrap_used,
+            reason = "attribute macro input is always a valid syn::Item"
+        )]
         let ts = match syn::parse(input).unwrap() {
             syn::Item::Const(item) => {
                 let idl_print = anchor_syn::idl::gen_idl_print_fn_constant(&item);
```

### lang/attribute/error/Cargo.toml
```diff
@@ -11,6 +11,13 @@ edition = "2021"
 [lib]
 proc-macro = true
 
+[lints.clippy]
+unwrap-used = "deny"
+expect-used = "deny"
+panic = "deny"
+unimplemented = "deny"
+indexing-slicing = "deny"
+
 [features]
 anchor-debug = ["anchor-syn/anchor-debug"]
 idl-build = ["anchor-syn/idl-build"]
```

### lang/attribute/error/src/lib.rs
```diff
@@ -62,7 +62,10 @@ pub fn error_code(
         false => Some(parse_macro_input!(args as ErrorArgs)),
     };
     let mut error_enum = parse_macro_input!(input as syn::ItemEnum);
-    let error = codegen::error::generate(error_parser::parse(&mut error_enum, args));
+    let error = match error_parser::parse(&mut error_enum, args) {
+        Ok(e) => codegen::error::generate(e),
+        Err(e) => e.into_compile_error(),
+    };
     proc_macro::TokenStream::from(error)
 }
 
```

### lang/attribute/event/Cargo.toml
```diff
@@ -12,6 +12,13 @@ edition = "2021"
 [lib]
 proc-macro = true
 
+[lints.clippy]
+unwrap-used = "deny"
+expect-used = "deny"
+panic = "deny"
+unimplemented = "deny"
+indexing-slicing = "deny"
+
 [features]
 anchor-debug = ["anchor-syn/anchor-debug"]
 event-cpi = ["anchor-syn/event-cpi"]
```

### lang/attribute/event/src/lib.rs
```diff
@@ -233,6 +233,10 @@ pub fn event_cpi(
     input: proc_macro::TokenStream,
 ) -> proc_macro::TokenStream {
     let accounts_struct = parse_macro_input!(input as syn::ItemStruct);
+    #[allow(
+        clippy::unwrap_used,
+        reason = "quote-generated struct tokens always parse"
+    )]
     let accounts_struct = add_event_cpi_accounts(&accounts_struct).unwrap();
     proc_macro::TokenStream::from(quote! {#accounts_struct})
 }
```

### lang/attribute/program/Cargo.toml
```diff
@@ -11,6 +11,13 @@ edition = "2021"
 [lib]
 proc-macro = true
 
+[lints.clippy]
+unwrap-used = "deny"
+expect-used = "deny"
+panic = "deny"
+unimplemented = "deny"
+indexing-slicing = "deny"
+
 [features]
 anchor-debug = ["anchor-syn/anchor-debug"]
 idl-build = ["anchor-syn/idl-build"]
```
