# [M] URL Parameter Injection in FDC Food Search API Causes Server Crash and Exposes Internal API Key

## Summary
Severity: Medium
Advisory: CVE-2026-33148
Aliases: GHSA-43p3-wx6h-9g7w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33148
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. In versions prior to 2.6.0, the FDC (USDA FoodData Central) search endpoint constructs an upstream API URL by directly interpolating the user-supplied `query` parameter into the URL string without URL-encoding. An attacker can inject additional URL parameters by including `&` characters in the query value. This allows overriding the API key, manipulating upstream query behavior, and causing server crashes (HTTP 500) via malformed requests — a Denial of Service condition. Version 2.6.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33148.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-43p3-wx6h-9g7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33148
