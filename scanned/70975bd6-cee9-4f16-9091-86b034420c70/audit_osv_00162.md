# [M] ALPINE-CVE-2016-6306

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-6306
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6306
Type: osv

## Affected
- Alpine:v3.2: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.3: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.4: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.5: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.6: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.7: `openssl` — affected >=0 <1.0.2i-r0
- Alpine:v3.8: `openssl` — affected >=0 <1.0.2i-r0

## Details
The certificate parser in OpenSSL before 1.0.1u and 1.0.2 before 1.0.2i might allow remote attackers to cause a denial of service (out-of-bounds read) via crafted certificate operations, related to s3_clnt.c and s3_srvr.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6306
