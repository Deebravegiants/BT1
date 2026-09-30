# [?] fix: tools/keymaster/requirements.txt to reduce vulnerabilities (#784)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2021-09-14
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/e3e1a49b71259ba3b22be110cf9027ae449ebd75
Type: security-commit

## Details
fix: tools/keymaster/requirements.txt to reduce vulnerabilities (#784)

The following vulnerabilities are fixed by pinning transitive dependencies:
- https://snyk.io/vuln/SNYK-PYTHON-WEBSOCKETS-1582792

## Patch
### tools/keymaster/requirements.txt
```diff
@@ -1,4 +1,5 @@
 click
 python-json-config
 web3
-prometheus_client
\ No newline at end of file
+prometheus_client
+websockets>=10.0 # not directly required, pinned by Snyk to avoid a vulnerability
\ No newline at end of file
```
