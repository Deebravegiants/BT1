# [H] ALPINE-CVE-2023-49285

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-49285
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-49285
Type: osv

## Affected
- Alpine:v3.19: `squid` — affected >=0 <6.5-r0
- Alpine:v3.20: `squid` — affected >=0 <6.5-r0
- Alpine:v3.21: `squid` — affected >=0 <6.5-r0
- Alpine:v3.22: `squid` — affected >=0 <6.5-r0
- Alpine:v3.23: `squid` — affected >=0 <6.5-r0
- Alpine:v3.24: `squid` — affected >=0 <6.5-r0

## Details
Squid is a caching proxy for the Web supporting HTTP, HTTPS, FTP, and more. Due to a Buffer Overread bug Squid is vulnerable to a Denial of Service attack against Squid HTTP Message processing. This bug is fixed by Squid version 6.5. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-49285
