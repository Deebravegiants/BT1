# [M] CVE-2025-55658

## Summary
Severity: Medium
Advisory: CVE-2025-55658
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2025-55658
Type: osv

## Details
GPAC MP4Box v2.4 was discovered to contain a floating point exception in the gf_opus_parse_packet_header function (media_tools/av_parsers.c). bThis vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted MP4 file.

## References
- https://infosec.exchange/@sigdevel/116710224797830572
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55658.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-55658
