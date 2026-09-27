# [H] The Addressing GLPI plugin allows data enumeration through uncontrolled object instantiation

## Summary
Severity: High
Advisory: CVE-2024-53850
Aliases: GHSA-fw42-79gw-7qr9
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L)
Published: 2024-12-26
Source: https://osv.dev/vulnerability/CVE-2024-53850
Type: osv

## Details
The Addressing GLPI plugin enables you to create IP reports for visualize IP addresses used and free on a given network.. Starting with 3.0.0 and before 3.0.3, a poor security check allows an unauthenticated attacker to determine whether data exists (by name) in GLPI.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53850.json
- https://github.com/pluginsGLPI/addressing/security/advisories/GHSA-fw42-79gw-7qr9
- https://nvd.nist.gov/vuln/detail/CVE-2024-53850
- https://github.com/pluginsGLPI/addressing/commit/b334187a99206abbd7d0bc84f720b0a6e69e92f0
