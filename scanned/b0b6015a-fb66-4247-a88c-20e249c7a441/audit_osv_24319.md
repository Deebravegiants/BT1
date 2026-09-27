# [M] Invalid certificate policies in leaf certificates are silently ignored

## Summary
Severity: Medium
Advisory: CVE-2023-0465
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-03-28
Source: https://osv.dev/vulnerability/CVE-2023-0465
Type: osv

## Details
Applications that use a non-default option when verifying certificates may be
vulnerable to an attack from a malicious CA to circumvent certain checks.

Invalid certificate policies in leaf certificates are silently ignored by
OpenSSL and other certificate policy checks are skipped for that certificate.
A malicious CA could use this to deliberately assert invalid certificate policies
in order to circumvent policy checking on the certificate altogether.

Policy processing is disabled by default but can be enabled by passing
the `-policy' argument to the command line utilities or by calling the
`X509_VERIFY_PARAM_set1_policies()' function.

## References
- https://lists.debian.org/debian-lts-announce/2023/06/msg00011.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0465.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0465
- https://security.gentoo.org/glsa/202402-08
- https://security.netapp.com/advisory/ntap-20230414-0001/
- https://www.debian.org/security/2023/dsa-5417
- https://www.openssl.org/news/secadv/20230328.txt
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=10325176f3d3e98c6e2b3bf5ab1e3b334de6947a
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=1dd43e0709fece299b15208f36cc7c76209ba0bb
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=b013765abfa80036dc779dd0e50602c57bb3bf95
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=facfb1ab745646e97a1920977ae4a9965ea61d5c
