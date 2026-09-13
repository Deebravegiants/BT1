# [H] JLSEC-2026-523

## Summary
Severity: High
Advisory: JLSEC-2026-523
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-523
Type: osv

## Affected
- Julia: `GnuTLS_jll` — affected >=0 <3.7.8+0

## Details
A vulnerability found in gnutls. This security flaw happens because of a double free error occurs during verification of pkcs7 signatures in `gnutls_pkcs7_verify` function.

## References
- https://access.redhat.com/security/cve/CVE-2022-2509
- https://lists.debian.org/debian-lts-announce/2022/08/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6FL27JS3VM74YEQU7PGB62USO3KSBYZX/
- https://lists.gnupg.org/pipermail/gnutls-help/2022-July/004746.html
- https://www.debian.org/security/2022/dsa-5203
