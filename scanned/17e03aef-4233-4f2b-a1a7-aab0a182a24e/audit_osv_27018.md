# [M] Recipes 1.5.10 - Blind SSRF

## Summary
Severity: Medium
Advisory: CVE-2024-0403
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-0403
Type: osv

## Details
Recipes version 1.5.10 allows arbitrary HTTP requests to be made

through the server. This is possible because the application is

vulnerable to SSRF.

## References
- https://github.com/TandoorRecipes/recipes/
- https://fluidattacks.com/advisories/harris/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0403.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0403
