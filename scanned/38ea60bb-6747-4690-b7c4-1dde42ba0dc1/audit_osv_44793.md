# [M] OpenMAIC before 1.0.1 SSRF via Environment-Gated URL Validation

## Summary
Severity: Medium
Advisory: CVE-2026-86259
Aliases: GHSA-9m7h-vh2h-rc3w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-06
Source: https://osv.dev/vulnerability/CVE-2026-86259
Type: osv

## Details
OpenMAIC before 1.0.1 skips server-side request forgery validation in non-production builds, allowing unauthenticated attackers to reach cloud instance metadata services. Attackers can supply arbitrary provider URLs via the x-base-url header or baseUrl parameter to access sensitive cloud credentials and metadata.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86259.json
- https://github.com/THU-MAIC/OpenMAIC/security/advisories/GHSA-9m7h-vh2h-rc3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-86259
- https://www.vulncheck.com/advisories/openmaic-before-1.0.1-ssrf-via-environment-gated-url-validation
- https://github.com/THU-MAIC/OpenMAIC/releases/tag/v1.0.1
- https://github.com/THU-MAIC/OpenMAIC
- https://github.com/THU-MAIC/OpenMAIC/blob/v1.0.0/app/api/generate/image/route.ts#L73-L78
- https://github.com/THU-MAIC/OpenMAIC/blob/v1.0.0/middleware.ts#L60-L63
