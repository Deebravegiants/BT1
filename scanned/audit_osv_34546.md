# [M] @plone/volto vulnerable to potential DoS by invoking specific URL by anonymous user

## Summary
Severity: Medium
Advisory: CVE-2025-61668
Aliases: GHSA-m8rj-ppph-mj33
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-02
Source: https://osv.dev/vulnerability/CVE-2025-61668
Type: osv

## Details
Volto is a ReactJS-based frontend for the Plone Content Management System. Versions 16.34.0 and below, 17.0.0 through 17.22.1, 18.0.0 through 18.27.1, and 19.0.0-alpha.1 through 19.0.0-alpha.5, an anonymous user could cause the NodeJS server part of Volto to quit with an error when visiting a specific URL. This issue is fixed in versions 16.34.1, 17.22.2, 18.27.2 and 19.0.0-alpha.6.

## References
- http://github.com/plone/volto/releases/tag/18.27.2
- https://github.com/plone/volto/releases/tag/16.34.1
- https://github.com/plone/volto/releases/tag/17.22.2
- https://github.com/plone/volto/releases/tag/19.0.0-alpha.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61668.json
- https://github.com/plone/volto/security/advisories/GHSA-m8rj-ppph-mj33
- https://nvd.nist.gov/vuln/detail/CVE-2025-61668
- https://github.com/plone/volto/commit/58d9f82d2d50ca9a87edbe16fed91762e57c109c
- https://github.com/plone/volto/pull/7412
- https://github.com/plone/volto/pull/7413
