# [H] ALPINE-CVE-2015-20107

## Summary
Severity: High
Advisory: ALPINE-CVE-2015-20107
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2022-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2015-20107
Type: osv

## Affected
- Alpine:v3.17: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.18: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.19: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.20: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.21: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.10.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.10.5-r0

## Details
In Python (aka CPython) up to 3.10.8, the mailcap module does not add escape characters into commands discovered in the system mailcap file. This may allow attackers to inject shell commands into applications that call mailcap.findmatch with untrusted input (if they lack validation of user-provided filenames or arguments). The fix is also back-ported to 3.7, 3.8, 3.9

## References
- https://security.alpinelinux.org/vuln/CVE-2015-20107
