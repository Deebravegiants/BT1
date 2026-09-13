# [C] Tandoor Recipes Vulnerable to Unrestricted Brute-Force via BasicAuthentication

## Summary
Severity: Critical
Advisory: CVE-2026-33152
Aliases: GHSA-7m7c-jjqc-r522
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33152
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. In versions prior to 2.6.0, Tandoor Recipes configures Django REST Framework with BasicAuthentication as one of the default authentication backends. The AllAuth rate limiting configuration (ACCOUNT_RATE_LIMITS: login: 5/m/ip) only applies to the HTML-based login endpoint at /accounts/login/. Any API endpoint that accepts authenticated requests can be targeted via Authorization: Basic headers with zero rate limiting, zero account lockout, and unlimited attempts. An attacker can perform high-speed password guessing against any known username. Version 2.6.0 patches the issue.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33152.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-7m7c-jjqc-r522
- https://nvd.nist.gov/vuln/detail/CVE-2026-33152
