# [C] Capgo - Scope Escalation via API Key Creation in /functions/v1/apikey

## Summary
Severity: Critical
Advisory: CVE-2026-56216
Aliases: GHSA-2ff8-7h96-hwfp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-20
Source: https://osv.dev/vulnerability/CVE-2026-56216
Type: osv

## Details
Capgo before 12.128.2 contains a scope escalation vulnerability in the POST /functions/v1/apikey endpoint that allows app-limited API keys to mint unrestricted keys by setting empty limits. Attackers with a compromised app-limited key can create an unrestricted key with org-wide access to resources like app listings and other protected endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56216.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-2ff8-7h96-hwfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-56216
- https://www.vulncheck.com/advisories/capgo-scope-escalation-via-api-key-creation-in-functions-v1-apikey
