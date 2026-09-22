# [M] ALPINE-CVE-2026-40205

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-40205
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-40205
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that holds an OAuth2 token granting only part of the required scopes can authenticate, because when more than one scope is required in the configuration, the remote token validation paths accept a token that carries only one of them, while the local token validation path correctly requires all of them. The configured authorization policy is not enforced, so a token that was granted only part of the required permissions is accepted where it should have been rejected. Use local token validation where tokens can be validated locally. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-40205
