# [?] fix(lsp): don't OOB when completing trait impl function (#12764)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-05-27
Source: https://github.com/noir-lang/noir/commit/c57d26a8c8faa4658fc05c40dcb502e5789c12e7
Type: security-commit

## Details
fix(lsp): don't OOB when completing trait impl function (#12764)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### tooling/lsp/src/requests/completion.rs
```diff
@@ -1376,8 +1376,8 @@ impl Visitor for NodeFinder<'_> {
                     while cursor < bytes.len() && bytes[cursor].is_ascii_whitespace() {
                         cursor += 1;
                     }
-                    let char = bytes[cursor] as char;
-                    if char != '(' && char != '<' {
+                    let char = bytes.get(cursor).copied().map(char::from);
+                    if !matches!(char, Some('(') | Some('<')) {
                         self.suggest_trait_impl_function(noir_trait_impl, noir_function);
                         return false;
                     }
```

### tooling/lsp/src/requests/completion/tests.rs
```diff
@@ -2605,6 +2605,29 @@ fn main() {
         .await;
     }
 
+    #[test]
+    async fn suggests_trait_impl_function_when_impl_does_not_have_closing_curly() {
+        let src = r#"
+        trait Trait {
+            fn foo(x: i32) -> i32;
+        }
+
+        struct Foo {}
+
+        impl Trait for Foo {
+            fn f>|<
+        "#;
+
+        assert_completion(
+            src,
+            vec![trait_impl_method_completion_item(
+                "fn foo(..)",
+                "foo(x: i32) -> i32 {\n    ${1}\n}",
+            )],
+        )
+        .await;
+    }
+
     #[test]
     async fn test_suggests_when_assignment_follows_in_chain_1() {
         let src = r#"
```
