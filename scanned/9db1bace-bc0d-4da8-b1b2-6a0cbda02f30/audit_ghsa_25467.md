# [H] Improper Input Validation in Apache Hadoop

## Summary
Severity: High
Advisory: GHSA-pr9x-qmp5-j3rr
CVE: CVE-2017-3162
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pr9x-qmp5-j3rr
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-client` — affected >=0 <2.7.0

## Details
HDFS clients interact with a servlet on the DataNode to browse the HDFS namespace. The NameNode is provided as a query parameter that is not validated in Apache Hadoop before 2.7.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-3162
- https://lists.apache.org/thread.html/r127f75748fcabc63bc5a1bec6885753eb9b2bed803b6ed7bd46f965b@%3Cuser.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r66de86b9a608c1da70b2d27d765c11ec88edf6e5dd6f379ab33e072a@%3Cuser.flink.apache.org%3E
- https://s.apache.org/k2ss
- http://www.securityfocus.com/bid/98017
