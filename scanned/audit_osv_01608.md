# [H] ALPINE-CVE-2019-5736

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-5736
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-02-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5736
Type: osv

## Affected
- Alpine:v3.10: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.11: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.12: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.13: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.14: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.15: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.16: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.17: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.18: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.19: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.20: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.21: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.22: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.23: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.24: `lxc` — affected >=0 <3.1.0-r1
- Alpine:v3.9: `lxc` — affected >=0 <3.1.0-r1

## Details
runc through 1.0-rc6, as used in Docker before 18.09.2 and other products, allows attackers to overwrite the host runc binary (and consequently obtain host root access) by leveraging the ability to execute a command as root within one of these types of containers: (1) a new container with an attacker-controlled image, or (2) an existing container, to which the attacker previously had write access, that can be attached with docker exec. This occurs because of file-descriptor mishandling, related to /proc/self/exe.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5736
