# [M] Libgcrypt before 1.12.2 sometimes allows a heap-based buffer overflow and denial of service via...

## Summary
Severity: Medium
Advisory: JLSEC-2026-496
Ecosystem: Julia
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/JLSEC-2026-496
Type: osv

## Affected
- Julia: `Libgcrypt_jll` — affected >=1.8.11+0 <1.12.2+0

## Details
Libgcrypt before 1.12.2 sometimes allows a heap-based buffer overflow and denial of service via crafted ECDH ciphertext to `gcry_pk_decrypt`.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://dev.gnupg.org/T8211
- https://github.com/advisories/GHSA-wrv8-79m2-qg24
- https://lists.gnupg.org/pipermail/gnupg-announce/2026q2/000503.html
- https://nvd.nist.gov/vuln/detail/CVE-2026-41989
- https://www.openwall.com/lists/oss-security/2026/04/21/1
