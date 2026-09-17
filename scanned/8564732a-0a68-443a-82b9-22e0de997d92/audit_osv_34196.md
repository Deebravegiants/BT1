# [H] CVE-2025-55657

## Summary
Severity: High
Advisory: CVE-2025-55657
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2025-55657
Type: osv

## Details
A NULL pointer dereference in the gf_odf_vvc_cfg_write_bs function (odf/descriptors.c) of GPAC MP4Box v2.4 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/13/16
- https://infosec.exchange/@sigdevel/116710754169365223
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55657.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55657
