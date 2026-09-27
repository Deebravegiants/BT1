# [M] Issue summary: Some non-default TLS server configurations can cause unbounded memory growth when...

## Summary
Severity: Medium
Advisory: JLSEC-2026-249
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-249
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=0 <3.0.15+0
- Julia: `Openresty_jll` — affected >=0 <1.27.1+0

## Details
Issue summary: Some non-default TLS server configurations can cause unbounded
memory growth when processing TLSv1.3 sessions

Impact summary: An attacker may exploit certain server configurations to trigger
unbounded memory growth that would lead to a Denial of Service

This problem can occur in TLSv1.3 if the non-default `SSL_OP_NO_TICKET` option is
being used (but not if `early_data` support is also configured and the default
anti-replay protection is in use). In this case, under certain conditions, the
session cache can get into an incorrect state and it will fail to flush properly
as it fills. The session cache will continue to grow in an unbounded manner. A
malicious client could deliberately create the scenario for this failure to
force a Denial of Service. It may also happen by accident in normal operation.

This issue only affects TLS servers supporting TLSv1.3. It does not affect TLS
clients.

The FIPS modules in 3.2, 3.1 and 3.0 are not affected by this issue. OpenSSL
1.0.2 is also not affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/04/08/5
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-354112.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-915275.html
- https://github.com/advisories/GHSA-299c-jvhc-gxj8
- https://github.com/openssl/openssl/commit/7e4d731b1c07201ad9374c1cd9ac5263bdf35bce
- https://github.com/openssl/openssl/commit/b52867a9f618bb955bed2a3ce3db4d4f97ed8e5d
- https://github.com/openssl/openssl/commit/e9d7083e241670332e0443da0f0d4ffb52829f08
- https://github.openssl.org/openssl/extended-releases/commit/5f8d25770ae6437db119dfc951e207271a326640
- https://lists.debian.org/debian-lts-announce/2024/10/msg00033.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00000.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-2511
- https://security.netapp.com/advisory/ntap-20240503-0013
- https://security.netapp.com/advisory/ntap-20240503-0013/
- https://www.openssl.org/news/secadv/20240408.txt
