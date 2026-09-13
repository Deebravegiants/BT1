# [H] A heap-based buffer over-read that might affect a system that compiles untrusted Lua code in turanszkij/WickedEngine.

## Summary
Severity: High
Advisory: CVE-2026-24821
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:H/SI:N/SA:H/S:N/AU:Y/R:U/V:D/RE:M/U:Amber)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24821
Type: osv

## Details
Out-of-bounds Read vulnerability in turanszkij WickedEngine (WickedEngine/LUA modules). This vulnerability is associated with program files lparser.C.

This issue affects WickedEngine: through 0.71.727.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24821.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24821
- https://github.com/turanszkij/WickedEngine/pull/1095
- https://github.com/turanszkij/WickedEngine
