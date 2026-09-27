# [M] NULL Pointer Dereference in libde265

## Summary
Severity: Medium
Advisory: CVE-2026-33164
Aliases: GHSA-wqrf-6rf5-v78r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33164
Type: osv

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.17, a malformed H.265 PPS NAL unit causes a segmentation fault in pic_parameter_set::set_derived_values(). This issue has been patched in version 1.0.17.

## References
- https://github.com/strukturag/libde265/releases/tag/v1.0.17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33164.json
- https://github.com/strukturag/libde265/security/advisories/GHSA-wqrf-6rf5-v78r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33164
