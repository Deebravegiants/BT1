# [M] Tandoor has a Stored CSS Injection via <style> Tag in Recipe Instructions (API-Level)

## Summary
Severity: Medium
Advisory: CVE-2026-35046
Aliases: GHSA-9hhh-g2fc-r8x2
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35046
Type: osv

## Details
Tandoor Recipes is an application for managing recipes, planning meals, and building shopping lists. Prior to 2.6.4, Tandoor Recipes allows authenticated users to inject arbitrary <style> tags into recipe step instructions. The bleach.clean() sanitizer explicitly whitelists the <style> tag, causing the backend to persist and serve unsanitized CSS payloads via the API. Any client consuming instructions_markdown from the API and rendering it as HTML without additional sanitization will execute attacker-controlled CSS — enabling UI redressing, phishing overlays, visual defacement, and CSS-based data exfiltration. This vulnerability is fixed in 2.6.4.

## References
- https://github.com/TandoorRecipes/recipes/releases/tag/2.6.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35046.json
- https://github.com/TandoorRecipes/recipes/security/advisories/GHSA-9hhh-g2fc-r8x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-35046
