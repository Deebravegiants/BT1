# [H] In Apache Kylin, Cross-origin requests with credentials are allowed to be sent from any origin.

## Summary
Severity: High
Advisory: GHSA-mgpf-hhgf-cxg4
CVE: CVE-2021-45457
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-mgpf-hhgf-cxg4
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=0 <3.1.3
- Maven: `org.apache.kylin:kylin` — affected >=4.0.0 <4.0.1

## Details
In Apache Kylin, Cross-origin requests with credentials are allowed to be sent from any origin. This issue affects Apache Kylin 2 version 2.6.6 and prior versions; Apache Kylin 3 version 3.1.2 and prior versions; Apache Kylin 4 version 4.0.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45457
- https://github.com/apache/kylin/pull/1781
- https://github.com/apache/kylin/pull/1782
- https://github.com/apache/kylin
- https://lists.apache.org/thread/rzv4mq58okwj1n88lry82ol2wwm57q1m
- http://www.openwall.com/lists/oss-security/2022/01/06/2
