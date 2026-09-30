# [C] ALPINE-CVE-2023-38408

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-38408
Ecosystem: Alpine:v3.16, Alpine:v3.17
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38408
Type: osv

## Affected
- Alpine:v3.16: `openssh` — affected >=0 <9.0_p1-r4
- Alpine:v3.17: `openssh` — affected >=0 <9.1_p1-r4

## Details
The PKCS#11 feature in ssh-agent in OpenSSH before 9.3p2 has an insufficiently trustworthy search path, leading to remote code execution if an agent is forwarded to an attacker-controlled system. (Code in /usr/lib is not necessarily safe for loading into ssh-agent.) NOTE: this issue exists because of an incomplete fix for CVE-2016-10009.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38408
