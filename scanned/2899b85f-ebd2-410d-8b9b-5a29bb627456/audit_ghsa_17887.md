# [M] OpenBao Login MFA Bypass of Rate Limiting and TOTP Token Reuse

## Summary
Severity: Medium
Advisory: GHSA-rxp7-9q75-vj3p
CVE: CVE-2025-55003
CWE: CWE-307
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-rxp7-9q75-vj3p
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0 <2.3.2
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250807113757-8340a6918f6c

## Details
### Impact

OpenBao's Login Multi-Factor Authentication (MFA) system allows enforcing MFA using Time-based One Time Password (TOTP). Due to normalization applied by the underlying TOTP library, codes were accepted which could contain whitespace; this whitespace could bypass internal rate limiting of the MFA method and allow reuse of existing MFA codes.

### Patches

OpenBao v2.3.2 will patch this issue.

### Workarounds

Use of rate-limiting quotas can limit an attacker's ability to exploit this: https://openbao.org/api-docs/system/rate-limit-quotas/

### References

This issue was disclosed to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-19-vault-login-mfa-bypass-of-rate-limiting-and-totp-token-reuse/76038
- https://nvd.nist.gov/vuln/detail/CVE-2025-6015

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-rxp7-9q75-vj3p
- https://nvd.nist.gov/vuln/detail/CVE-2025-55003
- https://nvd.nist.gov/vuln/detail/CVE-2025-6015
- https://github.com/openbao/openbao/commit/8340a6918f6c41d8f75b6c3845c376d9dc32ed19
- https://discuss.hashicorp.com/t/hcsec-2025-19-vault-login-mfa-bypass-of-rate-limiting-and-totp-token-reuse/76038
- https://github.com/openbao/openbao
