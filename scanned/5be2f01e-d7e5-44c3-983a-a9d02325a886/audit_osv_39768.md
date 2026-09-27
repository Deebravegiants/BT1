# [M] libheif has an incomplete fix for CVE-2026-3949: integer overflow bypass in vvdec_push_data2

## Summary
Severity: Medium
Advisory: CVE-2026-47251
Aliases: GHSA-p6q9-fhf2-vj9v
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-47251
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. The fix for CVE-2026-3949 (commit `b97c8b5`, PR #1712) introduced an integer overflow in the very security check it added. The check itself can be bypassed, allowing a crafted HEIF file with a VVC track to trigger the same out-of-bounds heap read that CVE-2026-3949 was meant to prevent. This is a separate, currently-unpatched vulnerability. Issue #1712 was closed as fixed without testing the edge case where `size` is near `UINT32_MAX`. Version 1.22.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47251.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-p6q9-fhf2-vj9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-47251
- https://github.com/strukturag/libheif/issues/1712
