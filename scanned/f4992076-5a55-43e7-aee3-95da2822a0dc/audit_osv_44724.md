# [H] xiaobei through 5.5.2 Unauthenticated Webhook Message Injection

## Summary
Severity: High
Advisory: CVE-2026-85667
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85667
Type: osv

## Details
xiaobei through 5.5.2 fails to implement authentication or signature validation on webhook endpoints, allowing unauthenticated attackers to inject arbitrary messages into the agent pipeline. Attackers can publish malicious messages via the /webhook_worktool handler and exploit unvalidated media URL fetching to perform server-side request forgery against internal services.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85667.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85667
- https://www.vulncheck.com/advisories/xiaobei-through-5.5.2-unauthenticated-webhook-message-injection
- https://github.com/TeamWiseFlow/xiaobei/issues/440
- https://github.com/TeamWiseFlow/xiaobei
- https://github.com/TeamWiseFlow/xiaobei/blob/v5.5.2/awada/awada-server/src/routes/webhook-worktool.ts
