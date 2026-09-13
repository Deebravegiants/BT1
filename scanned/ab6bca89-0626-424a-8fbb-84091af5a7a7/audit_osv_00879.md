# [M] ALPINE-CVE-2018-1000808

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-1000808
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000808
Type: osv

## Affected
- Alpine:v3.6: `py-openssl` — affected >=0 <17.5.0-r0
- Alpine:v3.7: `py-openssl` — affected >=0 <17.5.0-r0
- Alpine:v3.8: `py-openssl` — affected >=0 <17.5.0-r0

## Details
Python Cryptographic Authority pyopenssl version Before 17.5.0 contains a CWE - 401 : Failure to Release Memory Before Removing Last Reference vulnerability in PKCS #12 Store that can result in Denial of service if memory runs low or is exhausted. This attack appear to be exploitable via Depends upon calling application, however it could be as simple as initiating a TLS connection. Anything that would cause the calling application to reload certificates from a PKCS #12 store.. This vulnerability appears to have been fixed in 17.5.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000808
