# [M] Issue summary: Writing large, newline-free data into a BIO chain using the line-buffering filter...

## Summary
Severity: Medium
Advisory: JLSEC-2026-261
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-261
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.5+0
- Julia: `Openresty_jll` — affected >=0 <1.29.203+0

## Details
Issue summary: Writing large, newline-free data into a BIO chain using the
line-buffering filter where the next BIO performs short writes can trigger
a heap-based out-of-bounds write.

Impact summary: This out-of-bounds write can cause memory corruption which
typically results in a crash, leading to Denial of Service for an application.

The line-buffering BIO filter (`BIO_f_linebuffer`) is not used by default in
TLS/SSL data paths. In OpenSSL command-line applications, it is typically
only pushed onto stdout/stderr on VMS systems. Third-party applications that
explicitly use this filter with a BIO chain that can short-write and that
write large, newline-free data influenced by an attacker would be affected.
However, the circumstances where this could happen are unlikely to be under
attacker control, and `BIO_f_linebuffer` is unlikely to be handling non-curated
data controlled by an attacker. For that reason the issue was assessed as
Low severity.

The FIPS modules in 3.6, 3.5, 3.4, 3.3 and 3.0 are not affected by this issue,
as the BIO implementation is outside the OpenSSL FIPS module boundary.

OpenSSL 3.6, 3.5, 3.4, 3.3, 3.0, 1.1.1 and 1.0.2 are vulnerable to this issue.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://github.com/advisories/GHSA-g78j-46j5-97cr
- https://github.com/openssl/openssl/commit/384011202af92605d926fafe4a0bcd6b65d162ad
- https://github.com/openssl/openssl/commit/475c466ef2fbd8fc1df6fae1c3eed9c813fc8ff6
- https://github.com/openssl/openssl/commit/4c96fbba618e1940f038012506ee9e21d32ee12c
- https://github.com/openssl/openssl/commit/6845c3b6460a98b1ec4e463baa2ea1a63a32d7c0
- https://github.com/openssl/openssl/commit/68a7cd2e2816c3a02f4d45a2ce43fc04fac97096
- https://nvd.nist.gov/vuln/detail/CVE-2025-68160
- https://openssl-library.org/news/secadv/20260127.txt
