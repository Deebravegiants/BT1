# [M] Low-level invalid GF(2^m) parameters lead to OOB memory access

## Summary
Severity: Medium
Advisory: CVE-2024-9143
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-9143
Type: osv

## Details
Issue summary: Use of the low-level GF(2^m) elliptic curve APIs with untrusted
explicit values for the field polynomial can lead to out-of-bounds memory reads
or writes.

Impact summary: Out of bound memory writes can lead to an application crash or
even a possibility of a remote code execution, however, in all the protocols
involving Elliptic Curve Cryptography that we're aware of, either only "named
curves" are supported, or, if explicit curve parameters are supported, they
specify an X9.62 encoding of binary (GF(2^m)) curves that can't represent
problematic input values. Thus the likelihood of existence of a vulnerable
application is low.

In particular, the X9.62 encoding is used for ECC keys in X.509 certificates,
so problematic inputs cannot occur in the context of processing X.509
certificates.  Any problematic use-cases would have to be using an "exotic"
curve encoding.

The affected APIs include: EC_GROUP_new_curve_GF2m(), EC_GROUP_new_from_params(),
and various supporting BN_GF2m_*() functions.

Applications working with "exotic" explicit binary (GF(2^m)) curve parameters,
that make it possible to represent invalid field polynomials with a zero
constant term, via the above or similar APIs, may terminate abruptly as a
result of reading or writing outside of array bounds.  Remote code execution
cannot easily be ruled out.

The FIPS modules in 3.3, 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/10/16/1
- http://www.openwall.com/lists/oss-security/2024/10/23/1
- http://www.openwall.com/lists/oss-security/2024/10/24/1
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-277137.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00033.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00000.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9143.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9143
- https://openssl-library.org/news/secadv/20241016.txt
- https://security.netapp.com/advisory/ntap-20241101-0001/
- https://github.com/openssl/openssl/commit/72ae83ad214d2eef262461365a1975707f862712
- https://github.com/openssl/openssl/commit/bc7e04d7c8d509fb78fc0e285aa948fb0da04700
- https://github.com/openssl/openssl/commit/c0d3e4d32d2805f49bec30547f225bc4d092e1f4
- https://github.com/openssl/openssl/commit/fdf6723362ca51bd883295efe206cb5b1cfa5154
- https://github.openssl.org/openssl/extended-releases/commit/8efc0cbaa8ebba8e116f7b81a876a4123594d86a
- https://github.openssl.org/openssl/extended-releases/commit/9d576994cec2b7aa37a91740ea7e680810957e41
