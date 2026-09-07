# [C] resdata has Classic Buffer Overflow, Improper Validation of Array Index, NULL Pointer Dereference and Out-of-bounds Read

## Summary
Severity: Critical
Advisory: GHSA-pr85-w493-9w3x
CVE: CVE-2026-55209
CWE: CWE-120, CWE-125, CWE-129, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-pr85-w493-9w3x
Type: github-advisory

## Affected
- PyPI: `resdata` — affected >=0 <6.2.9

## Details
### Impact
Prior to version 6.2.9 resdata would not correctly validate input in GRDECL files. The severity rating assumes that resdata is used to parse untrused files in a networking context such as a webservice.

### Patches
The bug has been patched starting with version 6.2.9.

## References
- https://github.com/equinor/resdata/security/advisories/GHSA-pr85-w493-9w3x
- https://github.com/equinor/resdata
- https://github.com/equinor/resdata/releases/tag/6.2.9
