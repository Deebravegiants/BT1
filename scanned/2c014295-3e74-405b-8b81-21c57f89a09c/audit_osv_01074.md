# [H] ALPINE-CVE-2018-19158

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19158
Ecosystem: Alpine:v3.5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19158
Type: osv

## Affected
- Alpine:v3.5: `php5` — affected >=0 <5.6.39-r0

## Details
ColossusCoinXT through 1.0.5 (a chain-based proof-of-stake cryptocurrency) allows a remote denial of service, exploitable by an attacker who acquires even a small amount of stake/coins in the system. The attacker sends invalid headers/blocks, which are stored on the victim's disk.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19158
