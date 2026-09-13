# [M] OpenFGA subject to Information Disclosure via streamed-list-objects endpoint

## Summary
Severity: Medium
Advisory: GHSA-95x7-mh78-7w2r
CVE: CVE-2022-39340
CWE: CWE-285, CWE-862, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-95x7-mh78-7w2r
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <0.2.4

## Details
### Overview
During our internal security assessment, it was discovered that `streamed-list-objects` endpoint was not validating the authorization header resulting in the disclosure of objects in the store.

### Am I Affected?
You are affected by this vulnerability if you are using `openfga/openfga` version `v0.2.3` or prior and you are exposing the OpenFGA service to the internet.

### How to fix that?
Upgrade to version `v0.2.4`.

### Backward Compatibility
This update is backward compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-95x7-mh78-7w2r
- https://nvd.nist.gov/vuln/detail/CVE-2022-39340
- https://github.com/openfga/openfga/commit/779d73d4b6d067ee042ec9b59fec707eed71e42f
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v0.2.4
