# [C] Ruby Openssl Allows Incorrect Value Comparison

## Summary
Severity: Critical
Advisory: GHSA-mmrq-6999-72v8
CVE: CVE-2018-16395
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mmrq-6999-72v8
Type: github-advisory

## Affected
- RubyGems: `openssl` — affected >=0 <2.0.9
- RubyGems: `openssl` — affected >=2.1.0 <2.1.2

## Details
An issue was discovered in the OpenSSL library in Ruby when two `OpenSSL::X509::Name` objects are compared using `==`, depending on the ordering, non-equal objects may return true. When the first argument is one character longer than the second, or the second argument contains a character that is one less than a character in the same position of the first argument, the result of `==` will be true. This could be leveraged to create an illegitimate certificate that may be accepted as legitimate and then used in signing or encryption operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16395
- https://github.com/ruby/openssl/commit/f653cfa43f0f20e8c440122ea982382b6228e7f5
- https://hackerone.com/reports/387250
- https://www.ruby-lang.org/en/news/2018/11/06/ruby-2-6-0-preview3-released
- https://www.ruby-lang.org/en/news/2018/10/17/ruby-2-5-2-released
- https://www.ruby-lang.org/en/news/2018/10/17/ruby-2-4-5-released
- https://www.ruby-lang.org/en/news/2018/10/17/ruby-2-3-8-released
- https://www.ruby-lang.org/en/news/2018/10/17/openssl-x509-name-equality-check-does-not-work-correctly-cve-2018-16395
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.debian.org/security/2018/dsa-4332
- https://web.archive.org/web/20211206015239/https://securitytracker.com/id/1042105
- https://usn.ubuntu.com/3808-1
- https://security.netapp.com/advisory/ntap-20190221-0002
- https://lists.debian.org/debian-lts-announce/2018/10/msg00020.html
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openssl/CVE-2018-16395.yml
- https://access.redhat.com/errata/RHSA-2019:2565
- https://access.redhat.com/errata/RHSA-2019:1948
- https://access.redhat.com/errata/RHSA-2018:3738
- https://access.redhat.com/errata/RHSA-2018:3731
- https://access.redhat.com/errata/RHSA-2018:3730
