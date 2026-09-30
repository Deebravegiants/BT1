# [C] ALPINE-CVE-2017-7494

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-7494
Ecosystem: Alpine:v3.3, Alpine:v3.4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7494
Type: osv

## Affected
- Alpine:v3.3: `samba` — affected >=3.5.0 <4.2.14-r3
- Alpine:v3.4: `samba` — affected >=3.5.0 <4.4.14-r0

## Details
Samba since version 3.5.0 and before 4.6.4, 4.5.10 and 4.4.14 is vulnerable to remote code execution vulnerability, allowing a malicious client to upload a shared library to a writable share, and then cause the server to load and execute it.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7494
