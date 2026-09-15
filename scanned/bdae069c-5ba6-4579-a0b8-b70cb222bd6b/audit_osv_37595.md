# [C] Plunk has SSRF via unvalidated AWS SNS SubscriptionConfirmation in POST /webhooks/sns

## Summary
Severity: Critical
Advisory: CVE-2026-32096
Aliases: GHSA-xpqg-p8mp-7g44
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32096
Type: osv

## Details
Plunk is an open-source email platform built on top of AWS SES. Prior to 0.7.0, a Server-Side Request Forgery (SSRF) vulnerability existed in the SNS webhook handler. An unauthenticated attacker could send a crafted request that caused the server to make an arbitrary outbound HTTP GET request to any host accessible from the server. This vulnerability is fixed in 0.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32096.json
- https://github.com/useplunk/plunk/security/advisories/GHSA-xpqg-p8mp-7g44
- https://nvd.nist.gov/vuln/detail/CVE-2026-32096
- https://github.com/useplunk/plunk/commit/b8f1ad9ab53c78f8ef063fdc125f397c8bfc7652
