# [?] Remove the security email for vulnerability disclosure (#6495)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2026-05-05
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/6dd405a07fd94e7466bb573a909445efed0c3e55
Type: security-commit

## Details
Remove the security email for vulnerability disclosure (#6495)

## Patch
### SECURITY.md
```diff
@@ -1,6 +1,6 @@
 # Security Policy
 
-Security vulnerabilities should be disclosed to the project maintainers through [Immunefi], or alternatively by email to security@openzeppelin.com.
+Security vulnerabilities should be disclosed to the project maintainers through [Immunefi].
 
 [Immunefi]: https://immunefi.com/bounty/openzeppelin
 
```
