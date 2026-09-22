# [H] ALPINE-CVE-2019-14287

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14287
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14287
Type: osv

## Affected
- Alpine:v3.10: `sudo` — affected >=0 <1.8.27-r1
- Alpine:v3.11: `sudo` — affected >=0 <1.8.28-r0
- Alpine:v3.12: `sudo` — affected >=0 <1.8.28-r0
- Alpine:v3.13: `sudo` — affected >=0 <1.8.28-r0
- Alpine:v3.14: `sudo` — affected >=0 <1.8.28-r0
- Alpine:v3.15: `sudo` — affected >=0 <1.8.28-r0
- Alpine:v3.8: `sudo` — affected >=0 <1.8.23-r3
- Alpine:v3.9: `sudo` — affected >=0 <1.8.25_p1-r3

## Details
In Sudo before 1.8.28, an attacker with access to a Runas ALL sudoer account can bypass certain policy blacklists and session PAM modules, and can cause incorrect logging, by invoking sudo with a crafted user ID. For example, this allows bypass of !root configuration, and USER= logging, for a "sudo -u \#$((0xffffffff))" command.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14287
