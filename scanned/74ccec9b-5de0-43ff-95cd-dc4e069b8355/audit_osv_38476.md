# [M] CVE-2026-40227

## Summary
Severity: Medium
Advisory: CVE-2026-40227
Aliases: GHSA-848h-497j-8vjq
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40227
Type: osv

## Details
In systemd 260 before 261, a local unprivileged user can trigger an assert via an IPC API call with an array or map that has a null element.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40227.json
- https://github.com/systemd/systemd/security/advisories/GHSA-848h-497j-8vjq
- https://nvd.nist.gov/vuln/detail/CVE-2026-40227
