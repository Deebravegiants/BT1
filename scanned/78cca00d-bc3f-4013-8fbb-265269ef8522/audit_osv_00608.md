# [C] ALPINE-CVE-2017-2640

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-2640
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2640
Type: osv

## Affected
- Alpine:v3.2: `pidgin` — affected >=0 <2.10.11-r1
- Alpine:v3.3: `pidgin` — affected >=0 <2.10.11-r3
- Alpine:v3.4: `pidgin` — affected >=0 <2.11.0-r1
- Alpine:v3.5: `pidgin` — affected >=0 <2.11.0-r1

## Details
An out-of-bounds write flaw was found in the way Pidgin before 2.12.0 processed XML content. A malicious remote server could potentially use this flaw to crash Pidgin or execute arbitrary code in the context of the pidgin process.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2640
