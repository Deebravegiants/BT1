# [M] CVE-2025-55652

## Summary
Severity: Medium
Advisory: CVE-2025-55652
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-15
Source: https://osv.dev/vulnerability/CVE-2025-55652
Type: osv

## Details
A heap buffer overflow in the gf_isom_vp_config_new function (isomedia/avc_ext.c) of GPAC MP4Box v2.4 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/13/4
- https://infosec.exchange/@sigdevel/116736829161374790
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55652.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55652
