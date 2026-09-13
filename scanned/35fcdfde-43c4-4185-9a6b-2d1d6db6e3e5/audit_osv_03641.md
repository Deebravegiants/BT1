# [H] ALPINE-CVE-2026-3608

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-3608
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3608
Type: osv

## Affected
- Alpine:v3.22: `kea` — affected >=0 <2.6.5-r0
- Alpine:v3.23: `kea` — affected >=0 <3.0.3-r0
- Alpine:v3.24: `kea` — affected >=0 <3.0.3-r0

## Details
Sending a maliciously crafted message to the kea-ctrl-agent, kea-dhcp-ddns, kea-dhcp4, or kea-dhcp6 daemons over any configured API socket or HA listener can cause the receiving daemon to exit with a stack overflow error.
This issue affects Kea versions 2.6.0 through 2.6.4 and 3.0.0 through 3.0.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3608
