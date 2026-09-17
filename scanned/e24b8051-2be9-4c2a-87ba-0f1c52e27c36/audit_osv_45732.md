# [H] JLSEC-2026-266

## Summary
Severity: High
Advisory: JLSEC-2026-266
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-266
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.5.0+0 <3.5.4+0
- Julia: `Openresty_jll` — affected >=0 <1.29.203+0

## Details
Issue summary: An application trying to decrypt CMS messages encrypted using
password based encryption can trigger an out-of-bounds read and write.

Impact summary: This out-of-bounds read may trigger a crash which leads to
Denial of Service for an application. The out-of-bounds write can cause
a memory corruption which can have various consequences including
a Denial of Service or Execution of attacker-supplied code.

Although the consequences of a successful exploit of this vulnerability
could be severe, the probability that the attacker would be able to
perform it is low. Besides, password based (PWRI) encryption support in CMS
messages is very rarely used. For that reason the issue was assessed as
Moderate severity according to our Security Policy.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue, as the CMS implementation is outside the OpenSSL FIPS module
boundary.

## References
- http://www.openwall.com/lists/oss-security/2025/09/30/5
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-485750.html
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://github.com/openssl/openssl/commit/5965ea5dd6960f36d8b7f74f8eac67a8eb8f2b45
- https://github.com/openssl/openssl/commit/9e91358f365dee6c446dcdcdb01c04d2743fd280
- https://github.com/openssl/openssl/commit/a79c4ce559c6a3a8fd4109e9f33c1185d5bf2def
- https://github.com/openssl/openssl/commit/b5282d677551afda7d20e9c00e09561b547b2dfd
- https://github.com/openssl/openssl/commit/bae259a211ada6315dc50900686daaaaaa55f482
- https://github.openssl.org/openssl/extended-releases/commit/c2b96348bfa662f25f4fabf81958ae822063dae3
- https://github.openssl.org/openssl/extended-releases/commit/dfbaf161d8dafc1132dd88cd48ad990ed9b4c8ba
- https://lists.debian.org/debian-lts-announce/2025/10/msg00001.html
- https://openssl-library.org/news/secadv/20250930.txt
