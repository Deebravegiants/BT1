# [M] CVE-2026-40224

## Summary
Severity: Medium
Advisory: CVE-2026-40224
Aliases: GHSA-6pwp-j5vg-5j6m
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40224
Type: osv

## Details
In systemd 259 before 260, there is local privilege escalation in systemd-machined because varlink can be used to reach the root namespace.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40224.json
- https://github.com/systemd/systemd/security/advisories/GHSA-6pwp-j5vg-5j6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-40224
