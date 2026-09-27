# [M] ALPINE-CVE-2022-1343

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-1343
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-05-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1343
Type: osv

## Affected
- Alpine:v3.17: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.18: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.19: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.20: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.21: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.22: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.23: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.24: `openssl` — affected >=3.0.0 <3.0.3-r0
- Alpine:v3.15: `openssl3` — affected >=0 <3.0.3-r0
- Alpine:v3.16: `openssl3` — affected >=0 <3.0.3-r0

## Details
The function `OCSP_basic_verify` verifies the signer certificate on an OCSP response. In the case where the (non-default) flag OCSP_NOCHECKS is used then the response will be positive (meaning a successful verification) even in the case where the response signing certificate fails to verify. It is anticipated that most users of `OCSP_basic_verify` will not use the OCSP_NOCHECKS flag. In this case the `OCSP_basic_verify` function will return a negative value (indicating a fatal error) in the case of a certificate verification failure. The normal expected return value in this case would be 0. This issue also impacts the command line OpenSSL "ocsp" application. When verifying an ocsp response with the "-no_cert_checks" option the command line application will report that the verification is successful even though it has in fact failed. In this case the incorrect successful response will also be accompanied by error messages showing the failure and contradicting the apparently successful result. Fixed in OpenSSL 3.0.3 (Affected 3.0.0,3.0.1,3.0.2).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1343
