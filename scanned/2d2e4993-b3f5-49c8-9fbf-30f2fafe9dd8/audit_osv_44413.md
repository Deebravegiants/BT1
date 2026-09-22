# [M] Budibase Server before 3.41.3 SSRF with Credential Leakage

## Summary
Severity: Medium
Advisory: CVE-2026-82243
Aliases: GHSA-83m5-fvmg-r7xv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82243
Type: osv

## Details
Budibase Server before 3.41.3 contains a server-side request forgery vulnerability in the datasource verify endpoint that allows builder-level users to supply arbitrary URLs without SSRF validation. Attackers can exploit this to leak internal CouchDB credentials by making requests to attacker-controlled servers, gaining full database access in cloud deployments.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-83m5-fvmg-r7xv
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82243.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82243
- https://www.vulncheck.com/advisories/budibase-server-before-3.41.3-ssrf-with-credential-leakage
