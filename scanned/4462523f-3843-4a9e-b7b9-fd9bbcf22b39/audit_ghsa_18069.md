# [M] OpenBao TOTP Secrets Engine Code Reuse

## Summary
Severity: Medium
Advisory: GHSA-f7c3-mhj2-9pvg
CVE: CVE-2025-55000
CWE: CWE-156
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-f7c3-mhj2-9pvg
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0.1.0 <2.3.2
- Go: `github.com/openbao/openbao` — affected >=0 <0.0.0-20250806193153-183891f8d535

## Details
### Impact

OpenBao's TOTP secrets engine could accept valid codes multiple times rather than strictly-once. This was caused by unexpected normalization in the underlying TOTP library.

### Patches

OpenBao v2.3.2 will patch this issue.

In patching, codes which were not normalized (strictly N numeric digits) will now be rejected. This is a potentially breaking change.

### Workarounds

TOTP code verification is a privileged action; only trusted systems should be verifying codes. Ensure that all codes are first normalized before submitting to the OpenBao endpoint.

### References

This issue was disclosed to HashiCorp and is the OpenBao equivalent of the following tickets:

- https://discuss.hashicorp.com/t/hcsec-2025-17-vault-totp-secrets-engine-code-reuse/76036
- https://nvd.nist.gov/vuln/detail/CVE-2025-6014

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-f7c3-mhj2-9pvg
- https://nvd.nist.gov/vuln/detail/CVE-2025-55000
- https://nvd.nist.gov/vuln/detail/CVE-2025-6014
- https://github.com/openbao/openbao/commit/183891f8d535d5b6eb3d79fda8200cade6de99e1
- https://discuss.hashicorp.com/t/hcsec-2025-17-vault-totp-secrets-engine-code-reuse/76036
- https://github.com/openbao/openbao
