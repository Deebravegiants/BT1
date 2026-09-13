# [M] CVE-2025-55664

## Summary
Severity: Medium
Advisory: CVE-2025-55664
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2025-55664
Type: osv

## Details
A heap buffer overflow in the m2tsdmx_send_packet function (filters/dmx_m2ts.c) of GPAC MP4Box v2.4 allows attackers to cause a Denial of Service (DoS) via supplying a crafted MP4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/10
- https://infosec.exchange/@sigdevel/116659245751279377
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55664.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55664
- https://github.com/gpac/gpac/issues/3310
- https://github.com/gpac/gpac/commit/9bd6a72c9efc0513dfd33b87498afc7658dabd26
