# [?] Add Vyper Vulnerabilities and Exposures (VVE) List

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2019-05-24
Source: https://github.com/vyperlang/vyper/commit/b821e044a99420ce6ef51b942bae9db332105214
Type: security-commit

## Details
Add Vyper Vulnerabilities and Exposures (VVE) List

## Patch
### SECURITY.md
```diff
@@ -33,6 +33,11 @@ Please read prior audit reports for projects that use Vyper here:
 | ------- | ------- | ----------- |
 | Uniswap | 35038d2 | https://medium.com/consensys-diligence/uniswap-audit-b90335ac007 |
 
+## Known Vyper Vulnerabilities and Exposures (VVEs)
+
+| VVE | Description | Introduced | Fixed | Report Link |
+| --- | ----------- | ---------- | ----- | ----------- |
+
 ## Reporting a Vulnerability
 
 If you think you have found a security vulnerability with a project that has used Vyper,
```
