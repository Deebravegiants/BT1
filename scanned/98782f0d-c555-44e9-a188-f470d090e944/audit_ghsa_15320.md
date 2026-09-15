# [H] OpenFGA Authorization Bypass

## Summary
Severity: High
Advisory: GHSA-3f6g-m4hr-59h8
CVE: CVE-2024-42473
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-08-09
Source: https://github.com/advisories/GHSA-3f6g-m4hr-59h8
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.5.7 <1.5.9

## Details
## Overview

OpenFGA v1.5.7 and v1.5.8 are vulnerable to authorization bypass when calling Check API with a model that uses `but not` and `from` expressions and a userset. 

## Fix

- If you are using OpenFGA within Docker or as a Go library, as a binary, or through Docker, upgrade to v1.5.9 as soon as possible
- If using Helm chart, upgrade to 0.2.12 as soon as possible. 

This fix is backward compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-3f6g-m4hr-59h8
- https://nvd.nist.gov/vuln/detail/CVE-2024-42473
- https://github.com/openfga/openfga
