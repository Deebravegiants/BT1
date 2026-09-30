# [?] Add how users should report security vulnerabilities for this repository (#3071)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2021-09-03
Source: https://github.com/ChainSafe/lodestar/commit/a035e051564cf01da959901d606af156ec328db4
Type: security-commit

## Details
Add how users should report security vulnerabilities for this repository (#3071)

Suggestion to add a notice on how to report security vulnerabilities. This is visible at https://github.com/ChainSafe/lodestar/security

## Patch
### SECURITY.md
```diff
@@ -0,0 +1,11 @@
+# Security Policy
+
+## Supported Versions
+
+Please see [Releases](https://github.com/ChainSafe/lodestar/releases/). We recommend using the [most recently released version](https://github.com/ChainSafe/lodestar/releases/latest).
+
+## Reporting a Vulnerability
+
+Please send vulnerability reports to security@chainsafe.io.
+
+**Please do not file a public ticket** mentioning the vulnerability, as doing so could increase the likelihood of the vulnerability being used before a fix has been created, released and installed on the network.
```
