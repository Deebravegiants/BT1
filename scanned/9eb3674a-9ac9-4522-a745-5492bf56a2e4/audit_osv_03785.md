# [M] ALPINE-CVE-2026-4893

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-4893
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4893
Type: osv

## Affected
- Alpine:v3.22: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.23: `dnsmasq` — affected >=0 <2.91-r1
- Alpine:v3.24: `dnsmasq` — affected >=0 <2.92_p2-r0

## Details
An information disclosure vulnerability in dnsmasq allows remote attackers to bypass source checks via a crafted DNS packet with RFC 7871 client subnet information.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4893
