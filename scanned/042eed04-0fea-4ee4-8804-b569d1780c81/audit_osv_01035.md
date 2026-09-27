# [H] ALPINE-CVE-2018-16837

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-16837
Ecosystem: Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-16837
Type: osv

## Affected
- Alpine:v3.8: `ansible` — affected >=0 <2.5.11-r0
- Alpine:v3.9: `ansible` — affected >=0 <2.7.1-r0

## Details
Ansible "User" module leaks any data which is passed on as a parameter to ssh-keygen. This could lean in undesirable situations such as passphrases credentials passed as a parameter for the ssh-keygen executable. Showing those credentials in clear text form for every user which have access just to the process list.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-16837
