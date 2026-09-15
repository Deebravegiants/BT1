# [M] PEAR Has a Roadmap Authorization Bypass via Operator Precedence Bug

## Summary
Severity: Medium
Advisory: CVE-2026-25233
Aliases: GHSA-p92v-9j73-fxx3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25233
Type: osv

## Details
PEAR is a framework and distribution system for reusable PHP components. Prior to version 1.33.0, logic bug in the roadmap role check allows non-lead maintainers to create, update, or delete roadmaps. This issue has been patched in version 1.33.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25233.json
- https://github.com/pear/pearweb/security/advisories/GHSA-p92v-9j73-fxx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25233
