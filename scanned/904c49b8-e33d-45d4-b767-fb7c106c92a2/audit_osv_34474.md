# [M] CVE-2025-60485

## Summary
Severity: Medium
Advisory: CVE-2025-60485
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2025-60485
Type: osv

## Details
A segmentation violation in the gf_isom_apple_set_tag_ex function (/isomedia/isom_write.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/11
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/52/README.md
- https://infosec.exchange/@sigdevel/116662498332150083
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60485.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60485
- https://github.com/gpac/gpac/issues/3323
- https://github.com/gpac/gpac/commit/4860a1a6f128ccc9ae37b4b738d22029f9672457
