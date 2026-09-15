# [C] CVE-2021-40818

## Summary
Severity: Critical
Advisory: CVE-2021-40818
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-08
Source: https://osv.dev/vulnerability/CVE-2021-40818
Type: osv

## Details
scheme/webauthn.c in Glewlwyd SSO server through 2.5.3 has a buffer overflow during FIDO2 signature validation in webauthn registration.

## References
- https://bugs.debian.org/993867
- https://github.com/babelouest/glewlwyd/commit/0efd112bb62f566877750ad62ee828bff579b4e2
