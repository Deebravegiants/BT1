# [M] Fields GLPI plugin vulnerable to unauthorized write access to additional fields

## Summary
Severity: Medium
Advisory: CVE-2023-28855
Aliases: GHSA-52vv-hm4x-8584
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-28855
Type: osv

## Details
Fields is a GLPI plugin that allows users to add custom fields on GLPI items forms. Prior to versions 1.13.1 and 1.20.4, lack of access control check allows any authenticated user to write data to any fields container, including those to which they have no configured access. Versions 1.13.1 and 1.20.4 contain a patch for this issue.

## References
- https://github.com/pluginsGLPI/fields/releases/tag/1.13.1
- https://github.com/pluginsGLPI/fields/releases/tag/1.20.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28855.json
- https://github.com/pluginsGLPI/fields/security/advisories/GHSA-52vv-hm4x-8584
- https://nvd.nist.gov/vuln/detail/CVE-2023-28855
- https://github.com/pluginsGLPI/fields/commit/784260be7db185bb1e7d66b299997238c4c0205d
