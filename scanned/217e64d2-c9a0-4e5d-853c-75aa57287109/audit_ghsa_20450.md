# [H] Use of Hard-coded Credentials in Apache Kylin

## Summary
Severity: High
Advisory: GHSA-9fj5-jg6f-qg5r
CVE: CVE-2021-45458
CWE: CWE-326, CWE-330, CWE-798
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-9fj5-jg6f-qg5r
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=0 <3.1.3
- Maven: `org.apache.kylin:kylin` — affected >=4.0.0 <4.0.1

## Details
Apache Kylin provides encryption classes PasswordPlaceholderConfigurer to help users encrypt their passwords. In the encryption algorithm used by this encryption class, the cipher is initialized with a hardcoded key and IV. If users use class PasswordPlaceholderConfigurer to encrypt their password and configure it into kylin's configuration file, there is a risk that the password may be decrypted. This issue affects Apache Kylin 2 version 2.6.6 and prior versions; Apache Kylin 3 version 3.1.2 and prior versions; Apache Kylin 4 version 4.0.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45458
- https://github.com/apache/kylin/pull/1781
- https://github.com/apache/kylin/pull/1782
- https://github.com/apache/kylin
- https://lists.apache.org/thread/oof215qz188k16vhlo97cm1jksxdowfy
- http://www.openwall.com/lists/oss-security/2022/01/06/3
- http://www.openwall.com/lists/oss-security/2022/01/06/7
