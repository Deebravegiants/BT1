# [M] Regular expression denial of service in apache tika

## Summary
Severity: Medium
Advisory: GHSA-qw3f-w4pf-jh5f
CVE: CVE-2022-30973
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-01
Source: https://github.com/advisories/GHSA-qw3f-w4pf-jh5f
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-core` — affected >=1.17 <1.28.3

## Details
We failed to apply the fix for CVE-2022-30126 to the 1.x branch in the 1.28.2 release.  In Apache Tika, a regular expression in the StandardsText class, used by the StandardsExtractingContentHandler could lead to a denial of service caused by backtracking on a specially crafted file. This only affects users who are running the StandardsExtractingContentHandler, which is a non-standard handler.  This is fixed in 1.28.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30973
- https://github.com/apache/tika/commit/a36711610fa1f6f5ba0f594803415af795e0b265
- https://github.com/apache/tika/commit/e76302196ebcafb7b51fce37fbe8256e6c0fbc51
- https://github.com/advisories/GHSA-rpjm-422r-95mh
- https://github.com/apache/tika
- https://lists.apache.org/thread/gqvb5t4p7tmdpl0y5bdbf72pgxj04h7p
- https://security.netapp.com/advisory/ntap-20220722-0004
- http://www.openwall.com/lists/oss-security/2022/05/31/2
- http://www.openwall.com/lists/oss-security/2022/06/27/5
