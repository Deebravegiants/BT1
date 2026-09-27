# [H] Possible denial of service in X.509 name checks

## Summary
Severity: High
Advisory: CVE-2024-6119
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-6119
Type: osv

## Details
Issue summary: Applications performing certificate name checks (e.g., TLS
clients checking server certificates) may attempt to read an invalid memory
address resulting in abnormal termination of the application process.

Impact summary: Abnormal termination of an application can a cause a denial of
service.

Applications performing certificate name checks (e.g., TLS clients checking
server certificates) may attempt to read an invalid memory address when
comparing the expected name with an `otherName` subject alternative name of an
X.509 certificate. This may result in an exception that terminates the
application program.

Note that basic certificate chain validation (signatures, dates, ...) is not
affected, the denial of service can occur only when the application also
specifies an expected DNS name, Email address or IP address.

TLS servers rarely solicit client certificates, and even when they do, they
generally don't perform a name check against a reference identifier (expected
identity), but rather extract the presented identity after checking the
certificate chain.  So TLS servers are generally not affected and the severity
of the issue is Moderate.

The FIPS modules in 3.3, 3.2, 3.1 and 3.0 are not affected by this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/09/03/4
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://cert-portal.siemens.com/productcert/html/ssa-769027.html
- https://lists.freebsd.org/archives/freebsd-security/2024-September/000303.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6119.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6119
- https://openssl-library.org/news/secadv/20240903.txt
- https://security.netapp.com/advisory/ntap-20240912-0001/
- https://github.com/openssl/openssl/commit/05f360d9e849a1b277db628f1f13083a7f8dd04f
- https://github.com/openssl/openssl/commit/06d1dc3fa96a2ba5a3e22735a033012aadc9f0d6
- https://github.com/openssl/openssl/commit/621f3729831b05ee828a3203eddb621d014ff2b2
- https://github.com/openssl/openssl/commit/7dfcee2cd2a63b2c64b9b4b0850be64cb695b0a0
