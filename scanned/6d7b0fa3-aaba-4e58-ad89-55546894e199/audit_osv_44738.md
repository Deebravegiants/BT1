# [M] MegaParse 0.0.55 Server-Side Request Forgery via POST /v1/url

## Summary
Severity: Medium
Advisory: CVE-2026-85691
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85691
Type: osv

## Details
MegaParse 0.0.55 contains an unauthenticated server-side request forgery vulnerability in the POST /v1/url endpoint that fetches caller-supplied URLs server-side. Attackers can supply internal service URLs or metadata endpoints without authentication to read their responses directly from the JSON response.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85691.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85691
- https://www.vulncheck.com/advisories/megaparse-0.0.55-server-side-request-forgery-via-post-v1-url
- https://github.com/The-Vibe-Company/megaparse/issues/259
- https://github.com/The-Vibe-Company/megaparse
- https://github.com/The-Vibe-Company/megaparse/blob/megaparse-v0.0.55/libs/megaparse/src/megaparse/api/app.py
