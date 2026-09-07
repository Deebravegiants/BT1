# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-f4mm-2r69-mg5f
CVE: CVE-2022-39342
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-f4mm-2r69-mg5f
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <0.2.4

## Details
### Overview
During our internal security assessment, it was discovered that OpenFGA versions `v0.2.3` and prior are vulnerable to authorization bypass under certain conditions.

### Am I Affected?
You are affected by this vulnerability if you are using `openfga/openfga` version `v0.2.3` or prior, and your model has a relation defined as a tupleset (the right hand side of a ‘from’ statement) that involves anything other than a direct relationship (e.g. ‘as self’)

### How to fix that?
Upgrade to version `v0.2.4`.

### Backward Compatibility
This update is not backward compatible.
Any model involving rewritten tupleset relations will no longer be acceptable and has to be modified.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-f4mm-2r69-mg5f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39342
- https://github.com/openfga/openfga/commit/c8db1ee3d2a366f18e585dd33236340e76e784c4
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v0.2.4
