# [M] ALPINE-CVE-2017-7479

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-7479
Ecosystem: Alpine:v3.5, Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7479
Type: osv

## Affected
- Alpine:v3.5: `openvpn` — affected >=0 <2.3.15-r0
- Alpine:v3.6: `openvpn` — affected >=0 <2.4.2-r0

## Details
OpenVPN versions before 2.3.15 and before 2.4.2 are vulnerable to reachable assertion when packet-ID counter rolls over resulting into Denial of Service of server by authenticated attacker.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7479
