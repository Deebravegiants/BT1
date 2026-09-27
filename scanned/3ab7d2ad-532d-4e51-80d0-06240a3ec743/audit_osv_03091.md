# [H] ALPINE-CVE-2024-42365

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-42365
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-42365
Type: osv

## Affected
- Alpine:v3.17: `asterisk` — affected >=19.0.0 <18.24.3-r0
- Alpine:v3.18: `asterisk` — affected >=19.0.0 <18.24.3-r0
- Alpine:v3.19: `asterisk` — affected >=19.0.0 <20.9.3-r0
- Alpine:v3.20: `asterisk` — affected >=19.0.0 <20.9.2-r0
- Alpine:v3.21: `asterisk` — affected >=19.0.0 <20.9.2-r0
- Alpine:v3.22: `asterisk` — affected >=19.0.0 <20.9.2-r0
- Alpine:v3.23: `asterisk` — affected >=19.0.0 <20.9.2-r0
- Alpine:v3.24: `asterisk` — affected >=19.0.0 <20.9.2-r0

## Details
Asterisk is an open source private branch exchange (PBX) and telephony toolkit. Prior to asterisk versions 18.24.2, 20.9.2, and 21.4.2 and certified-asterisk versions 18.9-cert11 and 20.7-cert2, an AMI user with `write=originate` may change all configuration files in the `/etc/asterisk/` directory. This occurs because they are able to curl remote files and write them to disk, but are also able to append to existing files using the `FILE` function inside the `SET` application. This issue may result in privilege escalation, remote code execution and/or blind server-side request forgery with arbitrary protocol. Asterisk versions 18.24.2, 20.9.2, and 21.4.2 and certified-asterisk versions 18.9-cert11 and 20.7-cert2 contain a fix for this issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-42365
