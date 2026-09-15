# [H] ALPINE-CVE-2016-6515

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6515
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6515
Type: osv

## Affected
- Alpine:v3.2: `openssh` — affected >=0 <6.8_p1-r8
- Alpine:v3.3: `openssh` — affected >=0 <7.2_p2-r2
- Alpine:v3.4: `openssh` — affected >=0 <7.2_p2-r2

## Details
The auth_password function in auth-passwd.c in sshd in OpenSSH before 7.3 does not limit password lengths for password authentication, which allows remote attackers to cause a denial of service (crypt CPU consumption) via a long string.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6515
