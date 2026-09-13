# [C] Grav Flex Objects - Server-Side Template Injection via Dynamic Titles

## Summary
Severity: Critical
Advisory: CVE-2026-58655
Aliases: GHSA-623v-m3c4-3pw8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-58655
Type: osv

## Details
The bundled Grav Flex Objects plugin (getgrav/grav-plugin-flex-objects) before 1.4.0 contains a stored server-side template injection vulnerability. When rendering dynamic collection or object titles, the plugin passes user-controlled frontmatter values (page.header.flex.collection.title or page.header.flex.object.title) to Twig's template_from_string(), causing them to be evaluated as Twig code rather than treated as text. This path bypasses Grav's Security::cleanDangerousTwig() sanitization. An attacker who can control the title frontmatter of a publicly reachable Flex Objects page can achieve arbitrary Twig execution and escalate to remote command execution via access to internal Grav services such as the scheduler.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58655.json
- https://github.com/getgrav/grav/security/advisories/GHSA-623v-m3c4-3pw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-58655
- https://www.vulncheck.com/advisories/grav-flex-objects-server-side-template-injection-via-dynamic-titles
