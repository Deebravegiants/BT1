# [H] CVE-2025-52293

## Summary
Severity: High
Advisory: CVE-2025-52293
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2025-52293
Type: osv

## Details
A segmentation violaton in the gf_hevc_read_sps_bs_internal function (media_tools/av_parsers.c) of GPAC MP4Box v2.4 allows attackers to cause a Denial of Service (DoS) via supplying crafted HEVC SPS data.

## References
- http://www.openwall.com/lists/oss-security/2026/06/13/19
- https://infosec.exchange/@sigdevel/116710484148913883
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52293.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52293
