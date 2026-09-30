# [?] Ignore `RUSTSEC-2024-0344`

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-06-20
Source: https://github.com/casper-network/casper-node/commit/c1417ea9d8292c50ed913bc57d2c4f52296ba7fa
Type: security-commit

## Details
Ignore `RUSTSEC-2024-0344`

## Patch
### Makefile
```diff
@@ -145,7 +145,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit --ignore RUSTSEC-2024-0332
+	$(CARGO) audit --ignore RUSTSEC-2024-0332 --ignore RUSTSEC-2024-0344
 
 .PHONY: audit-as
 audit-as:
```
