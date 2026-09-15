# [M] Out of memory error when submitting the dataset form with a specially-crafted field

## Summary
Severity: Medium
Advisory: GHSA-7fgc-89cx-w8j5
CVE: CVE-2023-50248
CWE: CWE-130
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-7fgc-89cx-w8j5
Type: github-advisory

## Affected
- PyPI: `ckan` — affected >=2.0 <2.9.10
- PyPI: `ckan` — affected >=2.10.0 <2.10.3

## Details
### Impact

When submitting a POST request to the `/dataset/new` endpoint (including either the auth cookie or the `Authorization` header) with a specially-crafted field, an attacker can create an out-of-memory error in the hosting server.

To trigger this error the user needs to have permissions to create or edit datasets.

### Patches

This vulnerability has been patched in CKAN 2.10.3 and 2.9.10

## References
- https://github.com/ckan/ckan/security/advisories/GHSA-7fgc-89cx-w8j5
- https://nvd.nist.gov/vuln/detail/CVE-2023-50248
- https://github.com/ckan/ckan/commit/bd02018b65c5b81d7ede195d00d0fcbac3aa33be
- https://github.com/ckan/ckan
