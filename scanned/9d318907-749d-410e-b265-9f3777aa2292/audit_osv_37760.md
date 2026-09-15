# [H] Tandoor Recipes Vulnerable to Host Header Injection

## Summary
Severity: High
Advisory: CVE-2026-33149
Aliases: GHSA-x636-4jx6-xc4w
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33149
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Versions up to and including 2.5.3 set ALLOWED_HOSTS = '*' by default, which causes Django to accept any value in the HTTP Host header without validation. The application uses request.build_absolute_uri() to generate absolute URLs in multiple contexts, including invite link emails, API pagination, and OpenAPI schema generation. An attacker who can send requests to the application with a crafted Host header can manipulate all server-generated absolute URLs. The most critical impact is invite link poisoning: when an admin creates an invite and the application sends the invite email, the link points to the attacker's server instead of the real application. When the victim clicks the link, the invite token is sent to the attacker, who can then use it at the real application. As of time of publication, it is unknown if a patched version is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33149.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-x636-4jx6-xc4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33149
