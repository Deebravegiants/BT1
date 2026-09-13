# [C] FOSSBilling: Improper API Role Validation (system) Enables Unauthenticated Access to Privileged Admin Functions

## Summary
Severity: Critical
Advisory: CVE-2026-27604
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-27604
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Starting in version 0.5.4 and prior to version 0.8.0, an authorization bypass in the API role handling allows unauthenticated access to privileged `/api/system/*` endpoints. Because `system` resolves to the cron admin identity, attackers can invoke admin API methods without valid credentials, session, or CSRF token. Version 0.8.0 patches the issue. Some workarounds are available. Block external access to `/api/system/*` at reverse proxy/WAF, restrict API access by trusted source IPs only (`api.allowed_ips`), rotate all admin/client API tokens immediately, invalidate active sessions and reset high-privilege credentials, and/or review API request logs for suspicious `/api/system/` access and treat as potential incident.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27604.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-57mv-jm88-66jc
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-78x5-c8gw-8279
- https://nvd.nist.gov/vuln/detail/CVE-2026-27604
- https://www.vulncheck.com/blog/fossbilling-auth-bypass-ssti-rce
