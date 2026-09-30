# [M] alf.io has Improper Access Control for Organization Owners that Exposes System Secrets

## Summary
Severity: Medium
Advisory: CVE-2026-50165
Aliases: GHSA-x473-r8w6-fcq5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-50165
Type: osv

## Details
alf.io is an open source ticket reservation system for conferences, trade shows, workshops, and meetups. An Improper Access Control issue in versions prior to 2.0-M5-2605 allows an organization owner to read system-level configuration secrets through organization/event scoped "single configuration" endpoints. The affected endpoints require organization or event ownership, but they accept an arbitrary configuration key and then return the first matching value from a lookup that includes system-level configuration. As a result, an organization owner can retrieve secrets intended to be administrator-only, including the system API key when it is configured. Version 2.0-M5-2605 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50165.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-x473-r8w6-fcq5
- https://nvd.nist.gov/vuln/detail/CVE-2026-50165
