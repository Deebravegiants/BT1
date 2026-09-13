# [M] ALPINE-CVE-2016-2126

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-2126
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-05-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2126
Type: osv

## Affected
- Alpine:v3.2: `samba` — affected >=4.0.0 <4.2.14-r1
- Alpine:v3.3: `samba` — affected >=4.0.0 <4.2.14-r1
- Alpine:v3.4: `samba` — affected >=4.0.0 <4.4.5-r2

## Details
Samba version 4.0.0 up to 4.5.2 is vulnerable to privilege elevation due to incorrect handling of the PAC (Privilege Attribute Certificate) checksum. A remote, authenticated, attacker can cause the winbindd process to crash using a legitimate Kerberos ticket. A local service with access to the winbindd privileged pipe can cause winbindd to cache elevated access permissions.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2126
