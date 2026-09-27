# [H] OpenFGA Authorization Bypass

## Summary
Severity: High
Advisory: GHSA-8cph-m685-6v6r
CVE: CVE-2024-31452
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-8cph-m685-6v6r
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.5.0 <1.5.3

## Details
# Overview
Some end users of OpenFGA v1.5.0 or later are vulnerable to authorization bypass when calling Check or ListObjects APIs.

# Am I Affected?
You are very likely affected if your model involves exclusion (e.g. `a but not b`) or intersection (e.g. `a and b`) and you have any cyclical relationships. If you are using these, please update as soon as possible.

# Fix
Update to v1.5.3

# Backward Compatibility
This update is backward compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-8cph-m685-6v6r
- https://nvd.nist.gov/vuln/detail/CVE-2024-31452
- https://github.com/openfga/openfga/commit/b6a6d99b2bdbf8c3781503989576076289f48ed2
- https://github.com/openfga/openfga
