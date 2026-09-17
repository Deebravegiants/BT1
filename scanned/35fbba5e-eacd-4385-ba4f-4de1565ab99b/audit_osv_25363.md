# [M] Excessive time spent checking DH keys and parameters

## Summary
Severity: Medium
Advisory: CVE-2023-3446
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-07-19
Source: https://osv.dev/vulnerability/CVE-2023-3446
Type: osv

## Details
Issue summary: Checking excessively long DH keys or parameters may be very slow.

Impact summary: Applications that use the functions DH_check(), DH_check_ex()
or EVP_PKEY_param_check() to check a DH key or DH parameters may experience long
delays. Where the key or parameters that are being checked have been obtained
from an untrusted source this may lead to a Denial of Service.

The function DH_check() performs various checks on DH parameters. One of those
checks confirms that the modulus ('p' parameter) is not too large. Trying to use
a very large modulus is slow and OpenSSL will not normally use a modulus which
is over 10,000 bits in length.

However the DH_check() function checks numerous aspects of the key or parameters
that have been supplied. Some of those checks use the supplied modulus value
even if it has already been found to be too large.

An application that calls DH_check() and supplies a key or parameters obtained
from an untrusted source could be vulernable to a Denial of Service attack.

The function DH_check() is itself called by a number of other OpenSSL functions.
An application calling any of those other functions may similarly be affected.
The other functions affected by this are DH_check_ex() and
EVP_PKEY_param_check().

Also vulnerable are the OpenSSL dhparam and pkeyparam command line applications
when using the '-check' option.

The OpenSSL SSL/TLS implementation is not affected by this issue.
The OpenSSL 3.0 and 3.1 FIPS providers are not affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2023/07/19/4
- http://www.openwall.com/lists/oss-security/2023/07/19/5
- http://www.openwall.com/lists/oss-security/2023/07/19/6
- http://www.openwall.com/lists/oss-security/2023/07/31/1
- http://www.openwall.com/lists/oss-security/2024/05/16/1
- https://lists.debian.org/debian-lts-announce/2023/08/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3446.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3446
- https://security.gentoo.org/glsa/202402-08
- https://security.netapp.com/advisory/ntap-20230803-0011/
- https://www.openssl.org/news/secadv/20230719.txt
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=1fa20cf2f506113c761777127a38bce5068740eb
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=8780a896543a654e757db1b9396383f9d8095528
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=9a0a4d3c1e7138915563c0df4fe6a3f9377b839c
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=fc9867c1e03c22ebf56943be205202e576aabf23
