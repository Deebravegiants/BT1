# [H] CVE-2026-30997

## Summary
Severity: High
Advisory: CVE-2026-30997
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-30997
Type: osv

## Details
An out-of-bounds read in the read_global_param() function (libavcodec/av1dec.c) of FFmpeg v8.0.1 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://excellent-oatmeal-319.notion.site/CVE-2026-30997-Out-of-Bounds-Access-a7929817b9794568b2f7774397c7d65f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30997.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30997
- https://github.com/FFmpeg/FFmpeg
