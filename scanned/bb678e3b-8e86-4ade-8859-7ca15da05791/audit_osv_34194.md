# [M] CVE-2025-55651

## Summary
Severity: Medium
Advisory: CVE-2025-55651
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2025-55651
Type: osv

## Details
A NULL pointer dereference in the gf_isom_get_user_data_count function (isomedia/isom_read.c) of GPAC MP4Box v2.4 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/13/18
- https://infosec.exchange/@sigdevel/116710512103919834
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55651.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55651
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/4/4_poc.mp4
