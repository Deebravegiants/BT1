# [M] Helicone Cross-Tenant Provider Key Disclosure via Missing Organization Filter

## Summary
Severity: Medium
Advisory: CVE-2026-85178
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85178
Type: osv

## Details
Helicone's VaultManager.getDecryptedProviderKeyById() function in the GET /v1/vault/key/{providerKeyId} endpoint fails to validate the requester's organization against the vault key's organization identifier. Attackers with admin or owner privileges in any organization can retrieve decrypted upstream provider credentials for other tenants, including plaintext OpenAI, Anthropic, and Bedrock API keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85178.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85178
- https://www.vulncheck.com/advisories/helicone-cross-tenant-provider-key-disclosure-via-missing-organization-filter
- https://github.com/Helicone/helicone/issues/5712
- https://github.com/Helicone/helicone/commit/ca34549ea56f7ed587843f82d9cc19baa1f36ba4
- https://github.com/Helicone/helicone
