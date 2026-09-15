# [H] ALPINE-CVE-2026-48715

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48715
Ecosystem: Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48715
Type: osv

## Affected
- Alpine:v3.24: `radvd` — affected >=0 <2.21-r0

## Details
radvd is a router advertisement daemon for IPv6. Prior to version 2.21, the `radvdump` utility shipped with radvd contains a stack buffer overflow in the Route Information option parser. When processing a crafted ICMPv6 Router Advertisement, `print_ff()` copies up to 2032 bytes from attacker-controlled packet data into a 16-byte `struct in6_addr` on the stack, overflowing by up to 2016 bytes. Note that the main `radvd` daemon is not affected by the vulnerability. Version 2.21 patches the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48715
