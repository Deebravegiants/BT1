# [C] A heap-based buffer over-read or buffer overflow vulnerability in azerothcore/azerothcore-wotlk

## Summary
Severity: Critical
Advisory: CVE-2026-24793
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:N/AU:Y/R:U/V:C/RE:L/U:Red)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24793
Type: osv

## Details
Out-of-bounds Write, Buffer Copy without Checking Size of Input ('Classic Buffer Overflow') vulnerability in azerothcore azerothcore-wotlk (deps/zlib modules). This vulnerability is associated with program files inflate.C.

This issue affects azerothcore-wotlk: through v4.0.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24793.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24793
- https://github.com/azerothcore/azerothcore-wotlk/pull/21599
- https://github.com/azerothcore/azerothcore-wotlk
