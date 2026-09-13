# [M] Grav API Plugin before 1.0.10 Path Traversal via move

## Summary
Severity: Medium
Advisory: CVE-2026-65896
Aliases: GHSA-qjq4-jp55-4mx2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65896
Type: osv

## Details
Grav API Plugin (Composer package getgrav/grav-plugin-api) before 1.0.10 fails to properly validate the slug field in the POST /pages/{route}/move endpoint. PagesController::move() sanitizes the slug only with ltrim($body['slug'], '.'), which strips leading periods but does not neutralize '/' or '..' segments. An authenticated API caller with the api.pages.write permission can supply path traversal sequences (e.g., 01.home/../../../pwned) to move an entire page directory (content and media) to an arbitrary writable location outside user/pages/, including outside the Grav installation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65896.json
- https://github.com/getgrav/grav/security/advisories/GHSA-qjq4-jp55-4mx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-65896
- https://www.vulncheck.com/advisories/grav-api-plugin-before-path-traversal-via-move
- https://github.com/getgrav/grav-plugin-api/commit/f9438d4e71389b1041ac60b69b0b5714ecfa3bdd
