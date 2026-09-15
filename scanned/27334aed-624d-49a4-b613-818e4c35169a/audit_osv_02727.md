# [C] ALPINE-CVE-2022-45141

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-45141
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-45141
Type: osv

## Affected
- Alpine:v3.15: `samba` — affected >=4.16.0 <4.15.13-r0
- Alpine:v3.16: `samba` — affected >=4.16.0 <4.15.13-r0

## Details
Since the Windows Kerberos RC4-HMAC Elevation of Privilege Vulnerability was disclosed by Microsoft on Nov 8 2022 and per RFC8429 it is assumed that rc4-hmac is weak, Vulnerable Samba Active Directory DCs will issue rc4-hmac encrypted tickets despite the target server supporting better encryption (eg aes256-cts-hmac-sha1-96).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-45141
