# [M] ALPINE-CVE-2017-3735

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3735
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3735
Type: osv

## Affected
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2m-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2m-r0
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2m-r0
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2m-r0
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2m-r0
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2m-r0

## Details
While parsing an IPAddressFamily extension in an X.509 certificate, it is possible to do a one-byte overread. This would result in an incorrect text display of the certificate. This bug has been present since 2006 and is present in all versions of OpenSSL before 1.0.2m and 1.1.0g.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3735
