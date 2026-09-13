# [M] CVE-2025-60495

## Summary
Severity: Medium
Advisory: CVE-2025-60495
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2025-60495
Type: osv

## Details
A segmentation violation in the gf_media_get_color_info function (/media_tools/isom_tools.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted data file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/13
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/66/README.md
- https://infosec.exchange/@sigdevel/116659058320692913
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60495.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60495
- https://github.com/gpac/gpac/issues/3335
- https://github.com/gpac/gpac/commit/9beed3c0a2f38505c745e5376234e7ed66e8e0b1
