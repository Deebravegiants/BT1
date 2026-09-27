# [H] NULL Pointer Dereference in PKCS12_item_decrypt_d2i_ex function

## Summary
Severity: High
Advisory: CVE-2025-69421
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2025-69421
Type: osv

## Details
Issue summary: Processing a malformed PKCS#12 file can trigger a NULL pointer
dereference in the PKCS12_item_decrypt_d2i_ex() function.

Impact summary: A NULL pointer dereference can trigger a crash which leads to
Denial of Service for an application processing PKCS#12 files.

The PKCS12_item_decrypt_d2i_ex() function does not check whether the oct
parameter is NULL before dereferencing it. When called from
PKCS12_unpack_p7encdata() with a malformed PKCS#12 file, this parameter can
be NULL, causing a crash. The vulnerability is limited to Denial of Service
and cannot be escalated to achieve code execution or memory disclosure.

Exploiting this issue requires an attacker to provide a malformed PKCS#12 file
to an application that processes it. For that reason the issue was assessed as
Low severity according to our Security Policy.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the PKCS#12 implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are vulnerable to this issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69421.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69421
- https://openssl-library.org/news/secadv/20260127.txt
- https://github.com/openssl/openssl/commit/3524a29271f8191b8fd8a5257eb05173982a097b
- https://github.com/openssl/openssl/commit/36ecb4960872a4ce04bf6f1e1f4e78d75ec0c0c7
- https://github.com/openssl/openssl/commit/4bbc8d41a72c842ce4077a8a3eccd1109aaf74bd
- https://github.com/openssl/openssl/commit/643986985cd1c21221f941129d76fe0c2785aeb3
- https://github.com/openssl/openssl/commit/a2dbc539f0f9cc63832709fa5aa33ad9495eb19c
