# [H] ALPINE-CVE-2026-24031

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-24031
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-24031
Type: osv

## Affected
- Alpine:v3.23: `dovecot` — affected >=0 <2.4.3-r0
- Alpine:v3.24: `dovecot` — affected >=0 <2.4.3-r0

## Details
Dovecot SQL based authentication can be bypassed when auth_username_chars is cleared by admin. This vulnerability allows bypassing authentication for any user and user enumeration. Do not clear auth_username_chars. If this is not possible, install latest fixed version. No publicly available exploits are known.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-24031
