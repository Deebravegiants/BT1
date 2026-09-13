# [M] mreporting affected by a SQLI on date change

## Summary
Severity: Medium
Advisory: CVE-2026-22821
Aliases: GHSA-24q7-h59q-33w8
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-22821
Type: osv

## Details
mreporting is the more reporting GLPI plugin. Prior to 1.9.4, there is a possible SQL injection on date change. This vulnerability is fixed in 1.9.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22821.json
- https://github.com/pluginsGLPI/mreporting/security/advisories/GHSA-24q7-h59q-33w8
- https://nvd.nist.gov/vuln/detail/CVE-2026-22821
- https://github.com/pluginsGLPI/mreporting/commit/6f4a3caf9c1f7bbed1d910795d6e918d039f1f72
