# [M] @account-kit/smart-contracts Allowlist Module Bypass Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wfm2-rq5g-f8v5
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-wfm2-rq5g-f8v5
Type: github-advisory

## Affected
- npm: `@account-kit/smart-contracts` — affected >=4.8.0 <4.28.2

## Details
### Summary
Allowlist module contains a bypass vulnerability

### Details
The logic for using an allowlist on a Modular Account V2 contained a bug that allowed session keys to bypass any allowlist configuration

### Action
If you are using @aa-sdk and/or @account-kit/smart-contracts between the versions of >=4.8.0 and <4.28.1, please upgrade to 4.28.2

## References
- https://github.com/alchemyplatform/aa-sdk/security/advisories/GHSA-wfm2-rq5g-f8v5
- https://github.com/alchemyplatform/aa-sdk/commit/b65bafdb9eec3a009df2cbabf09a35a76550e9d0
- https://github.com/alchemyplatform/aa-sdk
