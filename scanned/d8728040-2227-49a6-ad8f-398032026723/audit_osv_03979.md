# [C] ALPINE-CVE-2026-8926

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-8926
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8926
Type: osv

## Affected
- Alpine:v3.23: `curl` — affected >=8.11.1 <8.22.0-r0
- Alpine:v3.24: `curl` — affected >=8.11.1 <8.21.0-r0

## Details
When asking curl to use a `.netrc` file to find credentials and at the same
time specifying a URL with a username(without a password), like
`https://user@example.com/`, curl could wrongly get and use the password for
*another* user set in the `.netrc` file for that host if such a one exists and
there is no match for the specified user.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8926
