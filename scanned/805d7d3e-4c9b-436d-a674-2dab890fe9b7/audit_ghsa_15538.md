# [M] Vault Leaks Client Token and Token Accessor in Audit Devices

## Summary
Severity: Medium
Advisory: GHSA-jjxf-26c9-77gm
CVE: CVE-2024-8365
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-02
Source: https://github.com/advisories/GHSA-jjxf-26c9-77gm
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/vault` — affected >=1.17.3 <1.17.5

## Details
Vault Community Edition and Vault Enterprise experienced a regression where functionality that HMAC’d sensitive headers in the configured audit device, specifically client tokens and token accessors, was removed. This resulted in the plaintext values of client tokens and token accessors being stored in the audit log. This vulnerability, CVE-2024-8365, was fixed in Vault Community Edition and Vault Enterprise 1.17.5 and Vault Enterprise 1.16.9.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8365
- https://discuss.hashicorp.com/t/hcsec-2024-18-vault-leaks-client-token-and-token-accessor-in-audit-devices
- https://github.com/advisories/GHSA-jjxf-26c9-77gm
- github.com/hashicorp/vault
