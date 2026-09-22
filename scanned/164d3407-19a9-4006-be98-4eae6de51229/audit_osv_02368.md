# [M] ALPINE-CVE-2022-0563

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-0563
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0563
Type: osv

## Affected
- Alpine:v3.12: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.13: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.14: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.15: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.16: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.17: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.18: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.19: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.20: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.21: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.22: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.23: `util-linux` — affected >=0 <2.37.4-r0
- Alpine:v3.24: `util-linux` — affected >=0 <2.37.4-r0

## Details
A flaw was found in the util-linux chfn and chsh utilities when compiled with Readline support. The Readline library uses an "INPUTRC" environment variable to get a path to the library config file. When the library cannot parse the specified file, it prints an error message containing data from the file. This flaw allows an unprivileged user to read root-owned files, potentially leading to privilege escalation. This flaw affects util-linux versions prior to 2.37.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0563
