# [H] SSRF via Jint Scripting Engine HTTP Functions Due to Missing SSRF Protection on "Jint" HttpClient

## Summary
Severity: High
Advisory: CVE-2026-41171
Aliases: GHSA-4m22-gvqm-jv97
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41171
Type: osv

## Details
Squidex is an open source headless content management system and content management hub. Versions prior to 7.23.0 have a Server-Side Request Forgery (SSRF) vulnerability due to missing SSRF protection on the `Jint` HTTP client used by scripting engine functions (`getJSON`, `request`, etc.). An authenticated user with low privileges (e.g., schema editing permissions) can force the server to make arbitrary outbound HTTP requests to attacker-controlled or internal endpoints. This allows access to internal services and cloud metadata endpoints (e.g., IMDS), potentially leading to credential exposure and lateral movement. Version 7.23.0 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41171.json
- https://github.com/Squidex/squidex/security/advisories/GHSA-4m22-gvqm-jv97
- https://nvd.nist.gov/vuln/detail/CVE-2026-41171
- https://github.com/Squidex/squidex/commit/b81d75e1d9c1a8e30993c2ee59b350002b9aeda4
