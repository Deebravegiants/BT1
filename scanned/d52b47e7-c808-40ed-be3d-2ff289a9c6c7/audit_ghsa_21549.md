# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-3gfj-fxx4-f22w
CVE: CVE-2022-39352
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-08
Source: https://github.com/advisories/GHSA-3gfj-fxx4-f22w
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <0.2.5

## Details
### Overview
During our internal security assessment, it was discovered that OpenFGA versions v0.2.4 and prior are vulnerable to authorization bypass under certain conditions.

### Am I Affected?
You are affected by this vulnerability if you are using `openfga/openfga` version v0.2.4 or prior, and have tuples where the `user` field is set to a `userset` e.g. `folder:test#owner`, and the tuple's relation is used on the right-hand side of a `from` statement.

### How to fix that?
Upgrade to version 0.2.5.

### Backward Compatibility
This update is not backward compatible.
Any tuples where the `user` field is set to a `userset`, and the tuple's relation is used on the right-hand side of a `from` statement have to be rewritten.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-3gfj-fxx4-f22w
- https://nvd.nist.gov/vuln/detail/CVE-2022-39352
- https://github.com/openfga/openfga/commit/776e80505e8d184b2286acc8268d8d74f36a9984
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v0.2.5
