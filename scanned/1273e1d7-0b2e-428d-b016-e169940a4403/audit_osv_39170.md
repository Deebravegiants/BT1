# [C] LinkWarden: Server-Side Request Forgery (SSRF) in Link Creation via fetchTitleAndHeaders Function

## Summary
Severity: Critical
Advisory: CVE-2026-44313
Aliases: GHSA-5qpc-x7rv-hvmp
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-44313
Type: osv

## Details
Linkwarden is a self-hosted, open-source collaborative bookmark manager to collect, organize and archive webpages. Prior to version 2.13.0, a Server-Side Request Forgery (SSRF) vulnerability in the fetchTitleAndHeaders function allows authenticated users to make arbitrary HTTP requests to internal services due to insufficient URL validation that only checks for "http://" or "https://" prefixes. This issue has been patched in version 2.13.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44313.json
- https://github.com/linkwarden/linkwarden/security/advisories/GHSA-5qpc-x7rv-hvmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44313
