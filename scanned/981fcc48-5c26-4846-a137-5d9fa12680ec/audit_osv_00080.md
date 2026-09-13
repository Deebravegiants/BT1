# [C] ALPINE-CVE-2016-2177

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-2177
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2177
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2h-r1
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2h-r1

## Details
OpenSSL through 1.0.2h incorrectly uses pointer arithmetic for heap-buffer boundary checks, which might allow remote attackers to cause a denial of service (integer overflow and application crash) or possibly have unspecified other impact by leveraging unexpected malloc behavior, related to s3_srvr.c, ssl_sess.c, and t1_lib.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2177
