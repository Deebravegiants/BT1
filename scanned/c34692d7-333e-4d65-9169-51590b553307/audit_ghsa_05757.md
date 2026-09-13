# [C] surfio has an out-of-bounds read

## Summary
Severity: Critical
Advisory: GHSA-rcr2-hggw-43wm
CVE: CVE-2026-55211
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-rcr2-hggw-43wm
Type: github-advisory

## Affected
- PyPI: `surfio` — affected >=0 <0.0.19

## Details
### Impact
Prior to version 0.0.19, surfio would not correctly validate size fields in irap files, leading to a buffer overflow . The severity rating assumes that surfio is used to parse untrused files in a networking context such as a web service.


### Patches
The bug has been patched in version 0.0.19

## References
- https://github.com/equinor/surfio/security/advisories/GHSA-rcr2-hggw-43wm
- https://github.com/equinor/surfio/pull/86
- https://github.com/equinor/surfio/commit/1619750bce28e39c4f378d2fb6d28b72380a12aa
- https://github.com/equinor/surfio
- https://github.com/equinor/surfio/releases/tag/0.0.19
