# [M] OpenProject: Insufficient access control leads to create Wiki objects belongs unpermitted projects

## Summary
Severity: Medium
Advisory: CVE-2026-27723
Aliases: GHSA-9gc6-3xjq-pwc9
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-27723
Type: osv

## Details
OpenProject is an open-source, web-based project management software. Prior to versions 17.0.5 and 17.1.2, an attacker can create wiki pages belonging to unpermitted projects through an improperly authenticated request. This issue has been patched in versions 17.0.5 and 17.1.2.

## References
- https://github.com/opf/openproject/releases/tag/v17.0.5
- https://github.com/opf/openproject/releases/tag/v17.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27723.json
- https://github.com/opf/openproject/security/advisories/GHSA-9gc6-3xjq-pwc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27723
