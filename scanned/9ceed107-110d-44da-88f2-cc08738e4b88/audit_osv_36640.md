# [C] A heap-based buffer over-read or buffer overflow vulnerability in FASTSHIFT/X-TRACK

## Summary
Severity: Critical
Advisory: CVE-2026-24823
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:N/AU:Y/R:U/V:C/RE:L/U:Red)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24823
Type: osv

## Details
Out-of-bounds Write, Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') vulnerability in FASTSHIFT X-TRACK (Software/X-Track/USER/App/Utils/lv_img_png/PNGdec/src modules). This vulnerability is associated with program files inflate.C.

This issue affects X-TRACK: through v2.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24823.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24823
- https://github.com/FASTSHIFT/X-TRACK/pull/120
- https://github.com/FASTSHIFT/X-TRACK
