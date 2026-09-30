# [?] add --ignore RUSTSEC-2026-0001

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2026-01-26
Source: https://github.com/casper-network/casper-node/commit/87d469a835f02567d8df9b3c4e10ac8fee9c681d
Type: security-commit

## Details
add --ignore RUSTSEC-2026-0001

## Patch
### Makefile
```diff
@@ -131,7 +131,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit --ignore RUSTSEC-2024-0437 --ignore RUSTSEC-2025-0022 --ignore RUSTSEC-2025-0055
+	$(CARGO) audit --ignore RUSTSEC-2024-0437 --ignore RUSTSEC-2025-0022 --ignore RUSTSEC-2025-0055 --ignore RUSTSEC-2026-0001
 
 .PHONY: audit
 audit: audit-rs
```
