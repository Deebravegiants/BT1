# [H] Tandoor Recipes - Local file disclosure - Users can read the content of any file on the server

## Summary
Severity: High
Advisory: CVE-2025-23212
Aliases: GHSA-jrgj-35jx-2qq7
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-01-28
Source: https://osv.dev/vulnerability/CVE-2025-23212
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. The external storage feature allows any user to enumerate the name and content of files on the server. This vulnerability is fixed in 1.5.28.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23212.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-jrgj-35jx-2qq7
- https://nvd.nist.gov/vuln/detail/CVE-2025-23212
- https://github.com/TandoorRecipes/recipes/commit/36e83a9d0108ac56b9538b45ead57efc8b97c5ff
