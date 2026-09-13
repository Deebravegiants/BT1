# [M] Papra has a Blind Server-Side Request Forgery (SSRF) via Webhook URL

## Summary
Severity: Medium
Advisory: CVE-2026-35461
Aliases: GHSA-cjw7-qg95-58mq
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-35461
Type: osv

## Details
Papra is a minimalistic document management and archiving platform. Prior to 26.4.0, the Papra webhook system allows authenticated users to register arbitrary URLs as webhook endpoints with no validation of the destination address. The server makes outbound HTTP POST requests to registered URLs, including localhost, internal network ranges, and cloud provider metadata endpoints, on every document event. This vulnerability is fixed in 26.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35461.json
- https://github.com/papra-hq/papra/security/advisories/GHSA-cjw7-qg95-58mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-35461
