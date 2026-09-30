# [?] fix(fmt): don't panic on stdin read failure (#11226)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-08-06
Source: https://github.com/foundry-rs/foundry/commit/a5eda9058462d598a219302e8031b443bc6fc78e
Type: security-commit

## Details
fix(fmt): don't panic on stdin read failure (#11226)

## Patch
### Makefile
```diff
@@ -150,4 +150,4 @@ dprint-check: ## Check formatting with dprint
 		echo "Installing dprint..."; \
 		cargo install dprint; \
 	fi
-	dprint check
\ No newline at end of file
+	dprint check
```

### crates/forge/src/cmd/fmt.rs
```diff
@@ -70,7 +70,7 @@ impl FmtArgs {
             }
             [one] if one == Path::new("-") => {
                 let mut s = String::new();
-                io::stdin().read_to_string(&mut s).expect("Failed to read from stdin");
+                io::stdin().read_to_string(&mut s).wrap_err("failed to read from stdin")?;
                 Input::Stdin(s)
             }
             paths => {
```
