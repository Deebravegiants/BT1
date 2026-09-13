# [H] ALPINE-CVE-2016-7045

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-7045
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7045
Type: osv

## Affected
- Alpine:v3.2: `irssi` — affected >=0 <0.8.20-r0
- Alpine:v3.3: `irssi` — affected >=0 <0.8.20-r0

## Details
The format_send_to_gui function in the format parsing code in Irssi before 0.8.20 allows remote attackers to cause a denial of service (heap corruption and crash) via vectors involving the length of a string.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7045
