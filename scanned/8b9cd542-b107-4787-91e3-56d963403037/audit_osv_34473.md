# [M] CVE-2025-60483

## Summary
Severity: Medium
Advisory: CVE-2025-60483
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2025-60483
Type: osv

## Details
A NULL pointer dereference in the gf_ac4_pres_b_4_back_channels_present function (/media_tools/av_parsers.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted AC4 file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/01/9
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/49/README.md
- https://infosec.exchange/@sigdevel/116659111520602254
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60483.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60483
- https://github.com/gpac/gpac/issues/3302
- https://github.com/gpac/gpac/commit/13eb5b76560aaf7813b865a2ad433258478e2695
