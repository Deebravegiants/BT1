# [M] Missing authentication in Aix-DB

## Summary
Severity: Medium
Advisory: CVE-2026-8335
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-8335
Type: osv

## Details
A missing authentication check on the Aix‑DB "/llm/process_llm_out" endpoint allows unauthenticated clients to execute arbitrary "SELECT" SQL queries and retrieve database data, as the endpoint lacks the token validation enforced on all other application endpoints.
All releases up to 1.2.4 are considered vulnerable. Status of next releases is unknown as the vulnerability has not been addressed by any patch.

## References
- https://cert.pl/posts/2026/06/CVE-2026-8335
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8335.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8335
- https://github.com/apconw/Aix-DB
