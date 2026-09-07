# [M] OpenBao's Inline Auth Incorrectly Redacted Headers

## Summary
Severity: Medium
Advisory: GHSA-q8cj-789h-vg24
CVE: CVE-2026-46358
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-q8cj-789h-vg24
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <2.5.4

## Details
### Impact

OpenBao's inline auth functionality incorrectly redacted audit log entries, resulting in non-auth headers being removed and auth-related headers being retained in cleartext. This requires an attacker to compromise access to the audit device. Operators should review leaked source authentication material and rotate it as appropriate.

### Patches

This is fixed in OpenBao v2.5.4.

### Resources

https://github.com/openbao/openbao/issues/3074

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-q8cj-789h-vg24
- https://github.com/openbao/openbao/issues/3074
- https://github.com/openbao/openbao/pull/3076
- https://github.com/openbao/openbao/commit/131c6966af4dfb4e1906703436eecdb8f2a3e9df
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.5.4
