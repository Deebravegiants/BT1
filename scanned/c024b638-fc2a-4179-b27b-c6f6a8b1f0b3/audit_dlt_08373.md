# [?] [coverage] prevent stack overflow in xtest's run of language/ir-testsuite's tests

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-10-05
Source: https://github.com/move-language/move/commit/5afee19deaa75559b3b864b4436d0c84403e478a
Type: security-commit

## Details
[coverage] prevent stack overflow in xtest's run of language/ir-testsuite's tests

Closes: #6375

## Patch
### devtools/x/src/test.rs
```diff
@@ -67,6 +67,8 @@ pub fn run(mut args: Args, xctx: XContext) -> Result<()> {
             ("RUSTC_BOOTSTRAP", "1"),
             // Recommend setting for grcov, avoids using the cargo cache.
             ("CARGO_INCREMENTAL", "0"),
+            // language/ir-testsuite's tests will stack overflow without this setting.
+            ("RUST_MIN_STACK", "8388608"),
             // Recommend flags for use with grcov, with these flags removed: -Copt-level=0, -Clink-dead-code.
             // for more info see:  https://github.com/mozilla/grcov#example-how-to-generate-gcda-fiels-for-a-rust-project
             (
```
