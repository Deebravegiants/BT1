# [H] Information Exposure in Apache Tapestry

## Summary
Severity: High
Advisory: GHSA-ghm8-mmx7-xvg2
CVE: CVE-2021-30638
CWE: CWE-200, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-ghm8-mmx7-xvg2
Type: github-advisory

## Affected
- Maven: `org.apache.tapestry:tapestry-core` — affected >=5.4.0 <5.6.4
- Maven: `org.apache.tapestry:tapestry-core` — affected >=5.7.0 <5.7.2

## Details
Information Exposure vulnerability in context asset handling of Apache Tapestry allows an attacker to download files inside WEB-INF if using a specially-constructed URL. This was caused by an incomplete fix for CVE-2020-13953. This issue affects Apache Tapestry Apache Tapestry 5.4.0 version to Apache Tapestry 5.6.3; Apache Tapestry 5.7.0 version and Apache Tapestry 5.7.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30638
- https://lists.apache.org/thread.html/r37dab61fc7f7088d4311e7f995ef4117d58d86a675f0256caa6991eb%40%3Cusers.tapestry.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210528-0004
- https://www.zerodayinitiative.com/advisories/ZDI-21-491
- http://www.openwall.com/lists/oss-security/2021/04/27/3
