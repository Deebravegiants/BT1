# [C] Apache Kylin vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-ppxx-m926-g569
CVE: CVE-2022-24697
CWE: CWE-77, CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-ppxx-m926-g569
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin-core-common` — affected >=0 <4.0.2
- Maven: `org.apache.kylin:kylin-spark-project` — affected >=0 <4.0.2
- Maven: `org.apache.kylin:kylin-server-base` — affected >=0 <4.0.2

## Details
Kylin's cube designer function has a command injection vulnerability when overwriting system parameters in the configuration overwrites menu. RCE can be implemented by closing the single quotation marks around the parameter value of “-- conf=” to inject any operating system command into the command line parameters. This vulnerability affects Kylin 2 version 2.6.5 and earlier, Kylin 3 version 3.1.2 and earlier, and Kylin 4 version 4.0.1 and earlier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24697
- https://github.com/apache/kylin/pull/1811
- https://github.com/apache/kylin
- https://lists.apache.org/thread/07mnn9c7o314wrhrwjr10w9j5s82voj4
- http://www.openwall.com/lists/oss-security/2022/12/30/1
