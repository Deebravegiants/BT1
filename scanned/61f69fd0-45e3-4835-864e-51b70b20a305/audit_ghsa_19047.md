# [H] OpenBao is Vulnerable to Privileged Operator Identity Group Root Escalation

## Summary
Severity: High
Advisory: GHSA-7ff4-jw48-3436
CVE: CVE-2025-64761
CWE: CWE-266, CWE-269
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-7ff4-jw48-3436
Type: github-advisory

## Affected
- Go: `github.com/openbao/openbao` — affected >=0 <2.4.4

## Details
### Impact

Similar to HCSEC-2025-13 / CVE-2025-5999, a privileged operator could use the identity group subsystem to add a root policy to a group identity group, escalating their or another user's permissions in the system. Specifically this is an issue when:

1. An operator in the root namespace has access to `identity/groups` endpoints.
2. An operator does not have policy access.

Otherwise, an operator with policy access could create or modify an existing policy to grant root-equivalent permissions through the `sudo` capability.

### Patches

Patched in version 2.4.4. 

### Workarounds

Users should audit the use of identity subsystem and deny operators access if it is not in use.

## References
- https://github.com/openbao/openbao/security/advisories/GHSA-7ff4-jw48-3436
- https://nvd.nist.gov/vuln/detail/CVE-2025-64761
- https://github.com/openbao/openbao/pull/2143
- https://github.com/openbao/openbao/commit/16bb0ccd37a502930a289d434cbe4e7b4edd66e5
- https://github.com/openbao/openbao/commit/747a1378c2756f86296ad9450f74f6faeecc2eb7
- https://github.com/openbao/openbao
- https://github.com/openbao/openbao/releases/tag/v2.4.4
