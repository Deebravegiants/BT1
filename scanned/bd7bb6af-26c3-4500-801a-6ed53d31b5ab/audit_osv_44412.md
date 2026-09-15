# [M] Budibase before 3.41.3 Cross-Application Resource Injection via Missing Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-82242
Aliases: GHSA-xqpq-288m-r5q7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82242
Type: osv

## Details
Budibase versions before 3.41.3 contain a missing authorization vulnerability in the POST /api/resources/duplicate endpoint that allows authenticated builders to inject tables, automations, queries, and screens into any other application without holding any role in the destination workspace. Attackers can inject resources by specifying an arbitrary destination workspace ID in the request body, then trigger injected automations with outgoing webhooks to exfiltrate data from victim applications.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-xqpq-288m-r5q7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82242.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82242
- https://www.vulncheck.com/advisories/budibase-before-3.41.3-cross-application-resource-injection-via-missing-authorization
