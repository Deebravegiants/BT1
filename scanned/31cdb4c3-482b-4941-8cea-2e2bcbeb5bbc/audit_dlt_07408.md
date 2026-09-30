# [?] fix(sol-macro-gen): don't panic on a $ in a Solidity contract name (#16581)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-09-03
Source: https://github.com/foundry-rs/foundry/commit/e7804d01234f156967a4eb59e4e051940a5521b4
Type: security-commit

## Details
fix(sol-macro-gen): don't panic on a $ in a Solidity contract name (#16581)

* fix(sol-macro-gen): don't panic on a $ in a Solidity contract name

`$` is legal in Solidity identifiers (IdentifierStart) but not in Rust
ones. forge bind panicked via proc_macro2::Ident::new when a contract
name containing $ reached SolMacroGen::get_sol_input.

Two layers:
- bind.rs's existing 'best effort identifier cleanup' (already handling
  whitespace and '-') now also strips '$', covering the only real
  production path into SolMacroGen::new.
- get_sol_input now parses the identifier via the fallible
  syn::parse_str instead of the panicking Ident::new, so a library
  consumer of forge-sol-macro-gen passing an uncleaned name gets a
  clean error instead of a crash.

New unit test confirms get_sol_input errors instead of panicking on an
invalid identifier. New end-to-end CLI test (bind_dollar_sign_in_contract_name)
creates a real contract named Foo$Bar, runs forge bind, and asserts the
generated bindings compile and contain no '$'.

* chore: add changelog entry

* test(forge): remove incomplete issue link

* chore: fix changelog package

Amp-Thread-ID: https://ampcode.com/threads/T-01a06539-2076-77bd-ab00-6ad184516295

* test(forge): simplify regression comment

---------

Co-authored-by: stevencartavia <112043913+stevencartavia@users.noreply.github.com>
Co-authored-by: steven <corderosteven6@gmail.com>
Co-authored-by: Mablr <59505383+mablr@users.noreply.github.com>

## Patch
### .changelog/fix-bind-dollar-sign-panic.md
```diff
@@ -0,0 +1,5 @@
+---
+forge: patch
+---
+
+Fixed `forge bind` panicking on a contract name containing `$`, which is a legal Solidity identifier character but not a legal Rust one.
```

### crates/forge/src/cmd/bind.rs
```diff
@@ -207,7 +207,7 @@ impl BindArgs {
                 let name = stem.split('.').next().unwrap();
 
                 // Best effort identifier cleanup.
-                let name = name.replace(char::is_whitespace, "").replace('-', "_");
+                let name = name.replace(char::is_whitespace, "").replace(['-', '$'], "_");
 
                 Some((name, path))
             })
```

### crates/forge/tests/cli/bind.rs
```diff
@@ -478,3 +478,28 @@ forgetest!(bind_single_file_crate_and_module_match, |prj, cmd| {
         fs::read(module_path.join("mod.rs")).unwrap()
     );
 });
+
+// `$` is valid in Solidity identifiers but not Rust identifiers; `forge bind` used to panic
+// instead of sanitizing it.
+forgetest!(bind_dollar_sign_in_contract_name, |prj, cmd| {
+    prj.add_source(
+        "Foo.sol",
+        r#"
+contract Foo$Bar {
+    uint256 public value;
+
+    function setValue(uint256 v) public {
+        value = v;
+    }
+}
+"#,
+    );
+
+    cmd.args(["bind"]).assert_success();
+
+    let bindings_path = prj.root().join("out/bindings");
+    let binding = fs::read_to_string(bindings_path.join("src/foo_bar.rs")).unwrap();
+    assert!(binding.contains("pub mod Foo_Bar"), "{binding}");
+    assert!(!binding.contains('$'), "{binding}");
+    assert_bindings_compile(&bindings_path);
+});
```

### crates/sol-macro-gen/src/sol_macro_gen.rs
```diff
@@ -48,7 +48,9 @@ impl SolMacroGen {
 
     pub fn get_sol_input(&self) -> Result<SolInput> {
         let path = self.path.to_string_lossy().into_owned();
-        let name = proc_macro2::Ident::new(&self.name, Span::call_site());
+        let name: syn::Ident = syn::parse_str(&self.name).wrap_err_with(|| {
+            format!("`{}` is not a valid Rust identifier for generated bindings", self.name)
+        })?;
         let tokens = quote::quote! {
             #[sol(ignore_unlinked)]
             #name,
@@ -556,4 +558,12 @@ mod tests {
             Some("::std::vec::Vec<[::serde_with::Same; 48]>".to_string())
         );
     }
+
+    #[test]
+    fn get_sol_input_rejects_invalid_identifier_instead_of_panicking() {
+        // `$` is valid in Solidity identifiers but not Rust identifiers.
+        let instance =
+            super::SolMacroGen::new(std::path::PathBuf::from("Foo.json"), "Foo$Bar".to_string());
+        assert!(instance.get_sol_input().is_err());
+    }
 }
```
