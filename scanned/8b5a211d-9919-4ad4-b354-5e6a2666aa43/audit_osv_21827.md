# [C] CVE-2021-46880

## Summary
Severity: Critical
Advisory: CVE-2021-46880
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2021-46880
Type: osv

## Details
x509/x509_verify.c in LibreSSL before 3.4.2, and OpenBSD before 7.0 errata 006, allows authentication bypass because an error for an unverified certificate chain is sometimes discarded.

## References
- https://ftp.openbsd.org/pub/OpenBSD/LibreSSL/libressl-3.4.2-relnotes.txt
- https://security.netapp.com/advisory/ntap-20230517-0006/
- https://ftp.openbsd.org/pub/OpenBSD/patches/7.0/common/006_x509.patch.sig
- https://github.com/openbsd/src/commit/3f851282810fa0ab4b90b3b1ecec2e8717ef16f8
