# [M] n8n before 1.123.69 Credential Leak via GraphQL Node Error

## Summary
Severity: Medium
Advisory: CVE-2026-77076
Aliases: GHSA-9fqj-7wc5-cwhx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77076
Type: osv

## Details
n8n versions before 1.123.69, 2.33.4, and 2.34.1 contain an information disclosure vulnerability in the GraphQL node. When a GraphQL request fails at the connection level, the node re-throws the underlying HTTP client error unchanged instead of wrapping it in n8n's standard error type. That error contains the live request's headers, including a decrypted credential secret, which the execution engine persists verbatim. Any authenticated user able to read the resulting execution can retrieve the decrypted credential secret from the stored run data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77076.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-9fqj-7wc5-cwhx
- https://nvd.nist.gov/vuln/detail/CVE-2026-77076
- https://www.vulncheck.com/advisories/n8n-before-credential-leak-via-graphql-node-error
