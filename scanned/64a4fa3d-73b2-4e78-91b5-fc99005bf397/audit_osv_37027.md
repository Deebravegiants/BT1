# [H] CVE-2026-27851

## Summary
Severity: High
Advisory: CVE-2026-27851
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-27851
Type: osv

## Details
When safe filter is used with variable expansion, all following pipelines on the same string are incorrectly interpreted as safe too, enabling unsafe data to be unescaped. This can enable SQL / LDAP injection attacks when used in authentication. Avoid using safe filter until on fixed version. No publicly available exploits are known.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27851.json
- https://access.redhat.com/security/cve/CVE-2026-27851
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0002.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27851.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27851
- https://bugzilla.redhat.com/show_bug.cgi?id=2476471
