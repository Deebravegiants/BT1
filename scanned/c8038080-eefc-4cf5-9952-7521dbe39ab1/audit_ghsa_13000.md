# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-jcf2-mxr2-gmqp
CVE: CVE-2023-40579
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-jcf2-mxr2-gmqp
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.3.1

## Details
## Overview
Some end users of OpenFGA v1.3.0 or earlier are vulnerable to authorization bypass when calling the ListObjects API. This means that the API sometimes returns more objects than it should.

## Am I Affected?
The vulnerability affects customers using ListObjects with specific models. The affected models contain expressions of type `rel1 from type1`.

## Fix
Update to v1.3.1.

## Backward Compatibility
This update is backward compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-jcf2-mxr2-gmqp
- https://nvd.nist.gov/vuln/detail/CVE-2023-40579
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.3.1
