# [M] Save stack space while handling errors in praydog/REFramework

## Summary
Severity: Medium
Advisory: CVE-2026-24809
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L/S:N/AU:Y/V:D/RE:M/U:Amber)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24809
Type: osv

## Details
An issue from the component luaG_runerror in dependencies/lua/src/ldebug.c in praydog/REFramework version before 1.5.5 leads to a heap-buffer overflow when a recursive error occurs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24809.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24809
- https://github.com/praydog/REFramework/pull/1320
- https://github.com/praydog/REFramework
