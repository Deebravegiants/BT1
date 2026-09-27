# [M] ALPINE-CVE-2020-25659

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25659
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-01-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25659
Type: osv

## Affected
- Alpine:v3.13: `py3-cryptography` — affected >=0 <3.2.1-r0
- Alpine:v3.14: `py3-cryptography` — affected >=0 <3.2.1-r0
- Alpine:v3.23: `py3-cryptography` — affected >=0 <3.2.1-r0
- Alpine:v3.24: `py3-cryptography` — affected >=0 <3.2.1-r0

## Details
python-cryptography 3.2 is vulnerable to Bleichenbacher timing attacks in the RSA decryption API, via timed processing of valid PKCS#1 v1.5 ciphertext.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25659
