# [H] CVE-2023-31486

## Summary
Severity: High
Advisory: CVE-2023-31486
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-31486
Type: osv

## Details
HTTP::Tiny before 0.083, a Perl core module since 5.13.9 and available standalone on CPAN, has an insecure default TLS configuration where users must opt in to verify certificates.

## References
- https://hackeriet.github.io/cpan-http-tiny-overview/
- https://www.openwall.com/lists/oss-security/2023/04/18/14
- https://www.openwall.com/lists/oss-security/2023/05/03/4
- https://www.reddit.com/r/perl/comments/111tadi/psa_httptiny_disabled_ssl_verification_by_default/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31486.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31486
- https://security.netapp.com/advisory/ntap-20241129-0011/
- https://github.com/chansen/p5-http-tiny/pull/153
- http://www.openwall.com/lists/oss-security/2023/04/29/1
- http://www.openwall.com/lists/oss-security/2023/05/03/3
- http://www.openwall.com/lists/oss-security/2023/05/03/5
- http://www.openwall.com/lists/oss-security/2023/05/07/2
- https://blog.hackeriet.no/perl-http-tiny-insecure-tls-default-affects-cpan-modules/
