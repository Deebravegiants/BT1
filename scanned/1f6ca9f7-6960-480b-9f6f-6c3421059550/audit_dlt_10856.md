# [?] [compiler] Fix compiler pre process source place holder replace panic bug. (#795)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-07-09
Source: https://github.com/starcoinorg/starcoin/commit/28815b60eb717bdfcef42b7bb99cc0c422d52cb2
Type: security-commit

## Details
[compiler] Fix compiler pre process source place holder replace panic bug. (#795)

## Patch
### vm/compiler/src/lib.rs
```diff
@@ -62,12 +62,14 @@ fn substitute_variable<S: ::std::hash::BuildHasher>(
     PAT.replace_all(text, |caps: &Captures| {
         let name = &caps[1];
         vars.get(name)
-            .unwrap_or_else(|| panic!("Can not find variable by name: {}", name))
+            .map(|s| s.to_string())
+            //if name not found, replace with origin place holder {{name}}, '{{' in format represent '{'
+            .unwrap_or_else(|| format!("{{{{{}}}}}", name))
     })
     .to_string()
 }
 
-//TODO find a gracefull method to do source file pre process and replace placeholders.
+//TODO find a graceful method to do source file pre process and replace placeholders.
 /// Replace {{variable}} placeholders in source file, default variable is `sender`.
 pub fn process_source_tpl<S: ::std::hash::BuildHasher>(
     source: &str,
@@ -201,6 +203,28 @@ mod tests {
     use starcoin_logger::prelude::*;
     use starcoin_vm_types::language_storage::CORE_CODE_ADDRESS;
 
+    #[test]
+    fn test_unknown_place_holder() {
+        let source_tpl = r#"
+        script{
+        use {{alice}}.MyModule;
+        fun main() {
+        }
+        }
+        "#;
+        let sender = parse_address("0x1dcd9f05cc902e4f342a404ade878efa").unwrap();
+        let mut vars = HashMap::new();
+        vars.insert("counter", format!("{}", 1));
+        let source = process_source_tpl(source_tpl, sender, vars);
+        //replace fail.
+        assert!(source.contains("{{alice}}"));
+        assert_eq!(
+            source_tpl,
+            source.as_str(),
+            "source tpl should equals source after replace fail."
+        );
+    }
+
     #[test]
     fn test_process_source_tpl() {
         let source_tpl = r#"
@@ -218,7 +242,6 @@ mod tests {
         let mut vars = HashMap::new();
         vars.insert("counter", format!("{}", 1));
         let source = process_source_tpl(source_tpl, sender, vars);
-        println!("{}", source);
         assert!(!source.contains("sender"))
     }
 
```
