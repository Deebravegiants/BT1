# [?] fix: tools/keymaster/requirements.txt to reduce vulnerabilities (#875)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2021-10-04
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/488b40c9d18166a21a0a1947cb747d28ad601fc0
Type: security-commit

## Details
fix: tools/keymaster/requirements.txt to reduce vulnerabilities (#875)

The following vulnerabilities are fixed by pinning transitive dependencies:
- https://snyk.io/vuln/SNYK-PYTHON-WEBSOCKETS-1582792

## Patch
### tools/keymaster/requirements.txt
```diff
@@ -2,4 +2,5 @@ click==8.0.1
 python-json-config==1.2.3
 web3==5.22.0
 prometheus-client==0.11.0
-backoff==1.11.1
\ No newline at end of file
+backoff==1.11.1
+websockets>=10.0 # not directly required, pinned by Snyk to avoid a vulnerability
\ No newline at end of file
```
