# [H] Tandoor Recipes affected by Blind SSRF with Internal Network Access via Recipe Import

## Summary
Severity: High
Advisory: CVE-2026-25991
Aliases: GHSA-j6xg-85mh-qqf7
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-25991
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.5.1, there is a Blind Server-Side Request Forgery (SSRF) vulnerability in the Cookmate recipe import feature of Tandoor Recipes. The application fails to validate the destination URL after following HTTP redirects, allowing any authenticated user (including standard users without administrative privileges) to force the server to connect to arbitrary internal or external resources. The vulnerability lies in cookbook/integration/cookmate.py, within the Cookmate integration class. This vulnerability can be leveraged to scan internal network ports, access cloud instance metadata (e.g., AWS/GCP Metadata Service), or disclose the server's real IP address. This vulnerability is fixed in 2.5.1.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.5.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25991.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-j6xg-85mh-qqf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25991
- https://github.com/TandoorRecipes/recipes/commit/fdf22c5e745740db1fec29d6b4bd3df5d340e6ab
