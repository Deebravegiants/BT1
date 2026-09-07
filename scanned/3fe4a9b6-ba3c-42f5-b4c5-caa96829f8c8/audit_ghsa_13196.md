# [C] Apache Axis 1.x (EOL) may allow RCE when untrusted input is passed to getService

## Summary
Severity: Critical
Advisory: GHSA-rmqp-9w4c-gc7w
CVE: CVE-2023-40743
CWE: CWE-20, CWE-75
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-05
Source: https://github.com/advisories/GHSA-rmqp-9w4c-gc7w
Type: github-advisory

## Affected
- Maven: `org.apache.axis:axis` — affected >=0
- Maven: `axis:axis` — affected >=0

## Details
When integrating Apache Axis 1.x in an application, it may not have been obvious that looking up a service through "ServiceFactory.getService" allows potentially dangerous lookup mechanisms such as LDAP. When passing untrusted input to this API method, this could expose the application to DoS, SSRF and even attacks leading to RCE.

As Axis 1 has been EOL we recommend you migrate to a different SOAP engine, such as Apache Axis 2/Java. As a workaround, you may review your code to verify no untrusted or unsanitized input is passed to "ServiceFactory.getService", or by applying the patch from  https://github.com/apache/axis-axis1-java/commit/7e66753427466590d6def0125e448d2791723210 . The Apache Axis project does not expect to create an Axis 1.x release fixing this problem, though contributors that would like to work towards this are welcome.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40743
- https://github.com/apache/axis-axis1-java/commit/7e66753427466590d6def0125e448d2791723210
- https://github.com/apache/axis-axis1-java
- https://lists.apache.org/thread/gs0qgk2mgss7zfhzdd6ftfjvm4kp7v82
- https://lists.debian.org/debian-lts-announce/2023/10/msg00025.html
