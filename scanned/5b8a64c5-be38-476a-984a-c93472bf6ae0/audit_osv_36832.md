# [M] Tandoor Recipes Affected by Authenticated Local File Disclosure (LFD) via Recipe Import leads to Arbitrary File Read

## Summary
Severity: Medium
Advisory: CVE-2026-25964
Aliases: GHSA-6485-jr28-52xx
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-25964
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.5.1, a Path Traversal vulnerability in the RecipeImport workflow of Tandoor Recipes allows authenticated users with import permissions to read arbitrary files on the server. This vulnerability stems from a lack of input validation in the file_path parameter and insufficient checks in the Local storage backend, enabling an attacker to bypass storage directory restrictions and access sensitive system files (e.g., /etc/passwd) or application configuration files (e.g., settings.py), potentially leading to full system compromise. This vulnerability is fixed in 2.5.1.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.5.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25964.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-6485-jr28-52xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-25964
- https://github.com/TandoorRecipes/recipes/commit/f7f3524609451ab0b5a4fd760ad0af147d8ed794
