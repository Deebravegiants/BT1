# [M] Out-of-bounds read in HTTP client no_proxy handling

## Summary
Severity: Medium
Advisory: CVE-2025-9232
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-9232
Type: osv

## Details
Issue summary: An application using the OpenSSL HTTP client API functions may
trigger an out-of-bounds read if the 'no_proxy' environment variable is set and
the host portion of the authority component of the HTTP URL is an IPv6 address.

Impact summary: An out-of-bounds read can trigger a crash which leads to
Denial of Service for an application.

The OpenSSL HTTP client API functions can be used directly by applications
but they are also used by the OCSP client functions and CMP (Certificate
Management Protocol) client implementation in OpenSSL. However the URLs used
by these implementations are unlikely to be controlled by an attacker.

In this vulnerable code the out of bounds read can only trigger a crash.
Furthermore the vulnerability requires an attacker-controlled URL to be
passed from an application to the OpenSSL function and the user has to have
a 'no_proxy' environment variable set. For the aforementioned reasons the
issue was assessed as Low severity.

The vulnerable code was introduced in the following patch releases:
3.0.16, 3.1.8, 3.2.4, 3.3.3, 3.4.0 and 3.5.0.

The FIPS modules in 3.5, 3.4, 3.3, 3.2, 3.1 and 3.0 are not affected by this
issue, as the HTTP client implementation is outside the OpenSSL FIPS module
boundary.

## References
- http://www.openwall.com/lists/oss-security/2025/09/30/5
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-485750.html
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9232.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-9232
- https://openssl-library.org/news/secadv/20250930.txt
- https://github.com/openssl/openssl/commit/2b4ec20e47959170422922eaff25346d362dcb35
- https://github.com/openssl/openssl/commit/654dc11d23468a74fc8ea4672b702dd3feb7be4b
- https://github.com/openssl/openssl/commit/7cf21a30513c9e43c4bc3836c237cf086e194af3
- https://github.com/openssl/openssl/commit/89e790ac431125a4849992858490bed6b225eadf
- https://github.com/openssl/openssl/commit/bbf38c034cdabd0a13330abcc4855c866f53d2e0
