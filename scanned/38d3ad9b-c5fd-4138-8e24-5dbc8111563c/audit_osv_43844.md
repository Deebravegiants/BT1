# [M] Predictable temporary file in /tmp allows symlink attack in LACT

## Summary
Severity: Medium
Advisory: CVE-2026-75038
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-75038
Type: osv

## Details
UNIX symbolic link (symlink) following vulnerability in ilya-zlobintsev/LACT allows for local denial-of-service. This issue affects LACT: through 0.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75038.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75038
- https://bugzilla.suse.com/show_bug.cgi?id=1276481
- https://github.com/ilya-zlobintsev/LACT
