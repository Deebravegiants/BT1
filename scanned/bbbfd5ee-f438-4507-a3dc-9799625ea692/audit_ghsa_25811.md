# [C] XML external entity (XXE) injection in Apache Nutch

## Summary
Severity: Critical
Advisory: GHSA-fxhp-wrw9-3r97
CVE: CVE-2021-23901
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-fxhp-wrw9-3r97
Type: github-advisory

## Affected
- Maven: `org.apache.nutch:nutch` — affected >=0 <1.18

## Details
An XML external entity (XXE) injection vulnerability was discovered in the Nutch DmozParser and is known to affect Nutch versions < 1.18. XML external entity injection (also known as XXE) is a web security vulnerability that allows an attacker to interfere with an application's processing of XML data. It often allows an attacker to view files on the application server filesystem, and to interact with any back-end or external systems that the application itself can access.  This issue is fixed in Apache Nutch 1.18.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23901
- https://github.com/apache/nutch/pull/563
- https://issues.apache.org/jira/browse/NUTCH-2841
- https://lists.apache.org/thread.html/r090321840b44cc91086c4e317bf2baffa270749dde6c1273b6567f7c%40%3Cdev.nutch.apache.org%3E
- https://lists.apache.org/thread.html/r5e2f7737b42c73a3325f3c2c8cdee1ec27631b3a0e144104d84d70e6@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r7ddfd680aa7ea001ca8da63bb23e3f8caa095a8b4f2261e46bade5c7@%3Cdev.nutch.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210513-0003
