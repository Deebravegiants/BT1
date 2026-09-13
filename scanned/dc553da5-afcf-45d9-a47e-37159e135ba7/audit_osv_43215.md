# [C] Budibase before 3.40.0 SQL Injection via Unauthenticated Webhook

## Summary
Severity: Critical
Advisory: CVE-2026-72851
Aliases: GHSA-x7h8-ww3q-xv7c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-72851
Type: osv

## Details
Budibase before 3.40.0 contains an unauthenticated SQL injection vulnerability in webhook-triggered automations with EXECUTE_QUERY steps. Attackers can POST attacker-controlled JSON to the webhook trigger endpoint to inject SQL payloads that execute with builder-configured database credentials, enabling data exfiltration, modification, and persistence in connected datasources like Snowflake.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-x7h8-ww3q-xv7c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72851.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72851
- https://www.vulncheck.com/advisories/budibase-before-sql-injection-via-unauthenticated-webhook
