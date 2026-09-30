# [?] Add how users should report security vulnerabilities for this repository (#9525)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2021-09-10
Source: https://github.com/OffchainLabs/prysm/commit/ffd7579476a78ca3d590bea9746df35bde619d81
Type: security-commit

## Details
Add how users should report security vulnerabilities for this repository (#9525)

* Add how users should report security vulnerabilities for this repository

Suggestion to add a notice on how to report security vulnerabilities. This is visible at https://github.com/prysmaticlabs/prysm/security

* Add correct email

Co-authored-by: Nishant Das <nish1993@hotmail.com>

* Update SECURITY.md

Co-authored-by: Nishant Das <nish1993@hotmail.com>
Co-authored-by: terence tsao <terence@prysmaticlabs.com>
Co-authored-by: Preston Van Loon <preston@prysmaticlabs.com>
Co-authored-by: Nishant Das <nishdas93@gmail.com>

## Patch
### SECURITY.md
```diff
@@ -0,0 +1,11 @@
+# Security Policy
+
+## Supported Versions
+
+[Releases](https://github.com/prysmaticlabs/prysm/releases/) contains all available releases. We recommend using the [most recently released version](https://github.com/prysmaticlabs/prysm/releases/latest).
+
+## Reporting a Vulnerability
+
+Please see our signed [security.txt](https://github.com/prysmaticlabs/prysm/blob/develop/.well-known/security.txt) for preferred encryption and reporting destination.
+
+**Please do not file a public ticket** mentioning the vulnerability, as doing so could increase the likelihood of the vulnerability being used before a fix has been created, released and installed on the network.
```
