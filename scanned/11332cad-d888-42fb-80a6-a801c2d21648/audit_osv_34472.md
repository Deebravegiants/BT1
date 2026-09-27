# [M] CVE-2025-60481

## Summary
Severity: Medium
Advisory: CVE-2025-60481
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2025-60481
Type: osv

## Details
A NULL pointer dereference in the gf_odf_ac4_cfg_dsi_v1 function (/odf/descriptors.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted AC4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/8
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/45/README.md
- https://infosec.exchange/@sigdevel/116659159345966316
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60481.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60481
- https://github.com/gpac/gpac/issues/3296
- https://github.com/gpac/gpac/commit/e02d1fd24cdc26acb1b236ab38b3832cffcae21b
