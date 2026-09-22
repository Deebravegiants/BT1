# [H] ALPINE-CVE-2024-4032

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-4032
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-4032
Type: osv

## Affected
- Alpine:v3.17: `python3` — affected >=0 <3.10.15-r0
- Alpine:v3.18: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.10-r0
- Alpine:v3.20: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.21: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.6-r0
- Alpine:v3.24: `python3` — affected >=0 <3.12.6-r0

## Details
The “ipaddress” module contained incorrect information about whether certain IPv4 and IPv6 addresses were designated as “globally reachable” or “private”. This affected the is_private and is_global properties of the ipaddress.IPv4Address, ipaddress.IPv4Network, ipaddress.IPv6Address, and ipaddress.IPv6Network classes, where values wouldn’t be returned in accordance with the latest information from the IANA Special-Purpose Address Registries.

CPython 3.12.4 and 3.13.0a6 contain updated information from these registries and thus have the intended behavior.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-4032
