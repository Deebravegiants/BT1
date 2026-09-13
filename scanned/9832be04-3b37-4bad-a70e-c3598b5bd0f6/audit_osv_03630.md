# [M] ALPINE-CVE-2026-34933

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-34933
Ecosystem: Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34933
Type: osv

## Affected
- Alpine:v3.24: `avahi` — affected >=0 <0.8-r26

## Details
Avahi is a system which facilitates service discovery on a local network via the mDNS/DNS-SD protocol suite. Prior to version 0.9-rc4, any unprivileged local user can crash avahi-daemon by sending a single D-Bus method call with conflicting publish flags. This issue has been patched in version 0.9-rc4.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34933
