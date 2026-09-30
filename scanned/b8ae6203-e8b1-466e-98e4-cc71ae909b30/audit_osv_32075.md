# [C] Tandoor Recipes - SSTI - Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-23211
Aliases: GHSA-r6rj-h75w-vj8v
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-01-28
Source: https://osv.dev/vulnerability/CVE-2025-23211
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. A Jinja2 SSTI vulnerability allows any user to execute commands on the server. In the case of the provided Docker Compose file as root. This vulnerability is fixed in 1.5.24.

## References
- https://github.com/TandoorRecipes/recipes/blob/4f9bff20c858180d0f7376de443a9fe4c123a50c/cookbook/helper/template_helper.py#L95
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23211.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-r6rj-h75w-vj8v
- https://nvd.nist.gov/vuln/detail/CVE-2025-23211
- https://github.com/TandoorRecipes/recipes/commit/e6087d5129cc9d0c24278948872377e66c2a2c20
