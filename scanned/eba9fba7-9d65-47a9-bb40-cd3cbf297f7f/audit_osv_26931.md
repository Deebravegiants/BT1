# [M] Excessive time spent checking invalid RSA public keys

## Summary
Severity: Medium
Advisory: CVE-2023-6237
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2023-6237
Type: osv

## Details
Issue summary: Checking excessively long invalid RSA public keys may take
a long time.

Impact summary: Applications that use the function EVP_PKEY_public_check()
to check RSA public keys may experience long delays. Where the key that
is being checked has been obtained from an untrusted source this may lead
to a Denial of Service.

When function EVP_PKEY_public_check() is called on RSA public keys,
a computation is done to confirm that the RSA modulus, n, is composite.
For valid RSA keys, n is a product of two or more large primes and this
computation completes quickly. However, if n is an overly large prime,
then this computation would take a long time.

An application that calls EVP_PKEY_public_check() and supplies an RSA key
obtained from an untrusted source could be vulnerable to a Denial of Service
attack.

The function EVP_PKEY_public_check() is not called from other OpenSSL
functions however it is called from the OpenSSL pkey command line
application. For that reason that application is also vulnerable if used
with the '-pubin' and '-check' options on untrusted data.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-331112.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-915275.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/6xxx/CVE-2023-6237.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-6237
- https://security.netapp.com/advisory/ntap-20240531-0007/
- https://www.openssl.org/news/secadv/20240115.txt
- https://github.com/openssl/openssl/commit/0b0f7abfb37350794a4b8960fafc292cd5d1b84d
- https://github.com/openssl/openssl/commit/18c02492138d1eb8b6548cb26e7b625fb2414a2a
- https://github.com/openssl/openssl/commit/a830f551557d3d66a84bbb18a5b889c640c36294
