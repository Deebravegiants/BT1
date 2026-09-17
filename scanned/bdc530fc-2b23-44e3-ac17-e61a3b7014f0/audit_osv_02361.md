# [H] ALPINE-CVE-2022-0336

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-0336
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-0336
Type: osv

## Affected
- Alpine:v3.15: `samba` — affected >=4.0.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.0.0 <4.15.12-r0

## Details
The Samba AD DC includes checks when adding service principals names (SPNs) to an account to ensure that SPNs do not alias with those already in the database. Some of these checks are able to be bypassed if an account modification re-adds an SPN that was previously present on that account, such as one added when a computer is joined to a domain. An attacker who has the ability to write to an account can exploit this to perform a denial-of-service attack by adding an SPN that matches an existing service. Additionally, an attacker who can intercept traffic can impersonate existing services, resulting in a loss of confidentiality and integrity.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-0336
