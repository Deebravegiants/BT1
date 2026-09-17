# [M] CVE-2026-41989

## Summary
Severity: Medium
Advisory: CVE-2026-41989
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-41989
Type: osv

## Details
Libgcrypt before 1.12.2 sometimes allows a heap-based buffer overflow and denial of service via crafted ECDH ciphertext to gcry_pk_decrypt.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://dev.gnupg.org/T8211
- https://lists.gnupg.org/pipermail/gnupg-announce/2026q2/000503.html
- https://www.openwall.com/lists/oss-security/2026/04/21/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41989.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41989
