# [M] OpenFGA denial of service

## Summary
Severity: Medium
Advisory: GHSA-rxpw-85vw-fx87
CVE: CVE-2024-23820
CWE: CWE-401, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-26
Source: https://github.com/advisories/GHSA-rxpw-85vw-fx87
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.4.3

## Details
## Overview
OpenFGA is vulnerable to a DoS attack. In some scenarios that depend on the model and tuples used, a call to ListObjects may not  release memory properly. So when a sufficiently high number of those calls are executed, the OpenFGA server can create an "out of memory" error and terminate.

## Fix
Upgrade to v1.4.3. This upgrade is backwards compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-rxpw-85vw-fx87
- https://nvd.nist.gov/vuln/detail/CVE-2024-23820
- https://github.com/openfga/openfga/commit/908ac85c8b7769c8042cca31886df8db01976c39
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.4.3
