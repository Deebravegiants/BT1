# [M] OpenFGA Authorization Bypass via tupleset wildcard

## Summary
Severity: Medium
Advisory: GHSA-vj4m-83m8-xpw5
CVE: CVE-2022-39341
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-vj4m-83m8-xpw5
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <0.2.4

## Details
### Overview
During our internal security assessment, it was discovered that OpenFGA versions `v0.2.3` and prior are vulnerable to authorization bypass under certain conditions.

### Am I affected?
You are affected by this vulnerability if you are using `openfga/openfga` version `v0.2.3` and you added a tuple with a wildcard (*) assigned to a tupleset relation (the right hand side of a ‘from’ statement).

### How to fix that?
Upgrade to version `v0.2.4`.

### Backward Compatibility
This update is not backward compatible with any authorization model that uses wildcard on a tupleset relation.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-vj4m-83m8-xpw5
- https://nvd.nist.gov/vuln/detail/CVE-2022-39341
- https://github.com/openfga/openfga/commit/b466769cc100b2065047786578718d313f52695b
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v0.2.4
