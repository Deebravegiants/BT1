# [?] Add how users should report security vulnerabilities for this repository (#2562)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2021-09-07
Source: https://github.com/sigp/lighthouse/commit/1eefd6d413b3a91cbdcbc104b17ea46264dcdd64
Type: security-commit

## Details
Add how users should report security vulnerabilities for this repository (#2562)

## Proposed Changes

Suggestion to add a notice on how to report security vulnerabilities. This is visible at https://github.com/sigp/lighthouse/security

## Patch
### SECURITY.md
```diff
@@ -0,0 +1,13 @@
+# Security Policy
+
+## Supported Versions
+
+Please see [Releases](https://github.com/sigp/lighthouse/releases/). We recommend using the [most recently released version](https://github.com/sigp/lighthouse/releases/latest).
+
+## Reporting a Vulnerability
+
+Please send vulnerability reports to security@sigmaprime.io and encrypt sensitive messages using our [PGP
+key](https://keybase.io/sigp/pgp_keys.asc?fingerprint=15e66d941f697e28f49381f426416dc3f30674b0).
+
+**Please do not file a public ticket** mentioning the vulnerability, as doing so could increase the likelihood of the vulnerability being used before a fix has been created, released and installed on the network.
+
```
