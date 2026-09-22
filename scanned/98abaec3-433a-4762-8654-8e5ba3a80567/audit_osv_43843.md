# [C] Polkit authentication bypass in LACT

## Summary
Severity: Critical
Advisory: CVE-2026-75037
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-75037
Type: osv

## Details
Polkit Authentication Based on UnixProcessSubject / Peer PID in LACT on Linux allows an Authentication Bypass. This issue affects LACT through 0.10.0. Fixed by commit d0478fe42c2219454e272f96b1cbd29ab37ee566.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75037.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75037
- https://bugzilla.suse.com/show_bug.cgi?id=1276480
- https://github.com/ilya-zlobintsev/LACT
