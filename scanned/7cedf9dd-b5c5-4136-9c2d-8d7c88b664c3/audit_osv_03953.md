# [H] ALPINE-CVE-2026-73208

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-73208
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73208
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.5-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.5-r0

## Details
An attacker that holds a token intended for a different purpose can authenticate, because when an OAuth2 token response does not contain a scope claim, the audience claim is used in its place and checked against the configured required scopes. These are different concepts, and the audience claim does not describe what a token is allowed to do. A token that grants no relevant permissions can be accepted because its intended recipient value happens to match a configured scope name, granting access that should have been denied. It also hides an identity provider misconfiguration where scopes are not being issued at all. Ensure the identity provider issues a scope claim for all tokens used with Dovecot, and that configured scope names do not match audience values. Update to non-vulnerable version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73208
