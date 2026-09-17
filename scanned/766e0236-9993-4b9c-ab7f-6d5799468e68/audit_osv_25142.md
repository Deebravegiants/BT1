# [M] CVE-2023-31485

## Summary
Severity: Medium
Advisory: CVE-2023-31485
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-28
Source: https://osv.dev/vulnerability/CVE-2023-31485
Type: osv

## Details
GitLab::API::v4 through 0.26 does not verify TLS certificates when connecting to a GitLab server, enabling machine-in-the-middle attacks.

## References
- https://www.openwall.com/lists/oss-security/2023/04/18/14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31485.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31485
- https://github.com/bluefeet/GitLab-API-v4/pull/57
- https://github.com/chansen/p5-http-tiny/pull/151
- http://www.openwall.com/lists/oss-security/2023/04/29/1
- http://www.openwall.com/lists/oss-security/2023/05/03/3
- http://www.openwall.com/lists/oss-security/2023/05/03/5
- http://www.openwall.com/lists/oss-security/2023/05/07/2
- https://blog.hackeriet.no/perl-http-tiny-insecure-tls-default-affects-cpan-modules/
