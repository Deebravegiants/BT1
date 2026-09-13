# [M] CVE-2026-40223

## Summary
Severity: Medium
Advisory: CVE-2026-40223
Aliases: GHSA-x4h8-rrrg-q78f
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40223
Type: osv

## Details
In systemd 258 before 260, a local unprivileged user can trigger an assert when a Delegate=yes and User=<unset> unit exists and is running.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40223.json
- https://github.com/systemd/systemd/security/advisories/GHSA-x4h8-rrrg-q78f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40223
