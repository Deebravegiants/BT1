# [M] Excessive time spent in DH check / generation with large Q parameter value

## Summary
Severity: Medium
Advisory: CVE-2023-5678
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-06
Source: https://osv.dev/vulnerability/CVE-2023-5678
Type: osv

## Details
Issue summary: Generating excessively long X9.42 DH keys or checking
excessively long X9.42 DH keys or parameters may be very slow.

Impact summary: Applications that use the functions DH_generate_key() to
generate an X9.42 DH key may experience long delays.  Likewise, applications
that use DH_check_pub_key(), DH_check_pub_key_ex() or EVP_PKEY_public_check()
to check an X9.42 DH key or X9.42 DH parameters may experience long delays.
Where the key or parameters that are being checked have been obtained from
an untrusted source this may lead to a Denial of Service.

While DH_check() performs all the necessary checks (as of CVE-2023-3817),
DH_check_pub_key() doesn't make any of these checks, and is therefore
vulnerable for excessively large P and Q parameters.

Likewise, while DH_generate_key() performs a check for an excessively large
P, it doesn't check for an excessively large Q.

An application that calls DH_generate_key() or DH_check_pub_key() and
supplies a key or parameters obtained from an untrusted source could be
vulnerable to a Denial of Service attack.

DH_generate_key() and DH_check_pub_key() are also called by a number of
other OpenSSL functions.  An application calling any of those other
functions may similarly be affected.  The other functions affected by this
are DH_check_pub_key_ex(), EVP_PKEY_public_check(), and EVP_PKEY_generate().

Also vulnerable are the OpenSSL pkey command line application when using the
"-pubcheck" option, as well as the OpenSSL genpkey command line application.

The OpenSSL SSL/TLS implementation is not affected by this issue.

The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/03/11/1
- https://cert-portal.siemens.com/productcert/html/ssa-093430.html
- https://cert-portal.siemens.com/productcert/html/ssa-128433.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-277137.html
- https://cert-portal.siemens.com/productcert/html/ssa-331112.html
- https://cert-portal.siemens.com/productcert/html/ssa-341067.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-556635.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://cert-portal.siemens.com/productcert/html/ssa-915275.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00033.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00000.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5678.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5678
- https://security.netapp.com/advisory/ntap-20231130-0010/
- https://www.openssl.org/news/secadv/20231106.txt
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=34efaef6c103d636ab507a0cc34dca4d3aecc055
