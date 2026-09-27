# [M] n8n: Log Streaming Event Destinations Decrypt Generic-Auth Credentials Without Ownership Check

## Summary
Severity: Medium
Advisory: CVE-2026-86993
Aliases: GHSA-pq6c-vh67-xpm3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86993
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 1.123.76, 2.37.7, and 2.38.2, a Log Streaming event destination could reference a generic HTTP credential and decrypt whichever credential ID it named without an ownership check. A user with a custom global role carrying Log Streaming scopes could select a credential belonging to another project and send its decrypted secret to an attacker-controlled endpoint. The affected authorization boundary is packages/cli/src/modules/log-streaming.ee/destinations/destination-credentials-access.ts and the credential:read scope. This issue is fixed in versions 1.123.76, 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.76
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86993.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-pq6c-vh67-xpm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-86993
