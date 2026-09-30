# [?] Bring back ignore of the `RUSTSEC-2024-0332`

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-05-16
Source: https://github.com/casper-network/casper-node/commit/59e0777e3816b425ef1bb3afefb06bc90f4fd5df
Type: security-commit

## Details
Bring back ignore of the `RUSTSEC-2024-0332`

## Patch
### Makefile
```diff
@@ -145,7 +145,7 @@ lint-smart-contracts:
 
 .PHONY: audit-rs
 audit-rs:
-	$(CARGO) audit
+	$(CARGO) audit --ignore RUSTSEC-2024-0332
 
 .PHONY: audit-as
 audit-as:
```
