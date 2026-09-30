# [?] Add ignore for RUSTSEC-2024-0437

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2025-03-10
Source: https://github.com/casper-network/casper-node/commit/d37e38c18cc42c763d0bddc9bbc6d25b62cada22
Type: security-commit

## Details
Add ignore for RUSTSEC-2024-0437

## Patch
### Makefile
```diff
@@ -132,7 +132,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit
+	$(CARGO) audit --ignore RUSTSEC-2024-0437
 
 .PHONY: audit
 audit: audit-rs
```
