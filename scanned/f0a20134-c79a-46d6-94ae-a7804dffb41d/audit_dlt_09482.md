# [?] Temporarily ignore RUSTSEC-2024-0371

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-09-09
Source: https://github.com/casper-network/casper-node/commit/8fdda4d5cd50237a1aab9d8fa94532536481c68e
Type: security-commit

## Details
Temporarily ignore RUSTSEC-2024-0371

## Patch
### Makefile
```diff
@@ -152,7 +152,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit --ignore RUSTSEC-2024-0344 --ignore RUSTSEC-2024-0367
+	$(CARGO) audit --ignore RUSTSEC-2024-0344 --ignore RUSTSEC-2024-0367 --ignore RUSTSEC-2024-0371
 
 .PHONY: audit-as
 audit-as:
```
