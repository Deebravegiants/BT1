# [H] ALPINE-CVE-2016-9952

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-9952
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9952
Type: osv

## Affected
- Alpine:v3.2: `curl` — affected >=7.30.0 <7.52.1-r0
- Alpine:v3.3: `curl` — affected >=7.30.0 <7.52.1-r0

## Details
The verify_certificate function in lib/vtls/schannel.c in libcurl 7.30.0 through 7.51.0, when built for Windows CE using the schannel TLS backend, makes it easier for remote attackers to conduct man-in-the-middle attacks via a crafted wildcard SAN in a server certificate, as demonstrated by "*.com."

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9952
