# [M] Apache Zeppelin SAP: connecting to a malicious SAP server allowed it to perform XXE

## Summary
Severity: Medium
Advisory: GHSA-rr59-h6rh-v84v
CVE: CVE-2022-47894
CWE: CWE-20, CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-09
Source: https://github.com/advisories/GHSA-rr59-h6rh-v84v
Type: github-advisory

## Affected
- Maven: `org.apache.zeppelin:sap` — affected >=0.8.0 <0.11.0

## Details
Improper Input Validation vulnerability in Apache Zeppelin SAP. This issue affects Apache Zeppelin SAP: from 0.8.0 before 0.11.0.

As this project is retired, we do not plan to release a version that fixes this issue. Users are recommended to find an alternative or restrict access to the instance to trusted users.

For more information, the fix already was merged in the source code but Zeppelin decided to retire the SAP component
NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-47894
- https://github.com/apache/zeppelin/pull/4302
- https://github.com/apache/zeppelin/commit/bea51d1467d6103bd8fd68d6a27b14f954d98ec6
- https://github.com/apache/zeppelin
- https://issues.apache.org/jira/browse/ZEPPELIN-5665
- https://lists.apache.org/thread/csf4k73kkn3nx58pm0p2qrylbox4fvyy
- http://www.openwall.com/lists/oss-security/2024/04/09/4
