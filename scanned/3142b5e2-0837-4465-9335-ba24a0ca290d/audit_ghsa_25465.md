# [M] Improper Neutralization of Input During Web Page Generation in Apache Hadoop

## Summary
Severity: Medium
Advisory: GHSA-qm7f-r83w-3p46
CVE: CVE-2017-3161
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qm7f-r83w-3p46
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-client` — affected >=0 <2.7.0

## Details
The HDFS web UI in Apache Hadoop before 2.7.0 is vulnerable to a cross-site scripting (XSS) attack through an unescaped query parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3161
- https://lists.apache.org/thread.html/r127f75748fcabc63bc5a1bec6885753eb9b2bed803b6ed7bd46f965b@%3Cuser.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r66de86b9a608c1da70b2d27d765c11ec88edf6e5dd6f379ab33e072a@%3Cuser.flink.apache.org%3E
- https://s.apache.org/4MQm
- http://www.securityfocus.com/bid/98025
