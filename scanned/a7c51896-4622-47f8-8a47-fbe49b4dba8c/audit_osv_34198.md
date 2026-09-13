# [M] CVE-2025-55659

## Summary
Severity: Medium
Advisory: CVE-2025-55659
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2025-55659
Type: osv

## Details
A NULL pointer dereference in the ctts_box_write function (isomedia/box_code_base.c) of GPAC MP4Box v2.4 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/13/17
- https://infosec.exchange/@sigdevel/116710743410087676
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55659.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55659
