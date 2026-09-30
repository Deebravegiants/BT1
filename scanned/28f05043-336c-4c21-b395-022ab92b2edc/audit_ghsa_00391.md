# [C] Apache Tika allows Java code execution for serialized objects embedded in MATLAB files

## Summary
Severity: Critical
Advisory: GHSA-j8g6-2wh7-6439
CVE: CVE-2016-6809
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-17
Source: https://github.com/advisories/GHSA-j8g6-2wh7-6439
Type: github-advisory

## Affected
- Maven: `org.apache.tika:tika-core` — affected >=0 <1.14

## Details
Apache Tika before 1.14 allows Java code execution for serialized objects embedded in MATLAB files. The issue exists because Tika invokes JMatIO to do native deserialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6809
- https://github.com/apache/tika/commit/8a68b5d474205cc91cbbb610d4a1c05af57f0610
- https://dist.apache.org/repos/dist/release/tika/CHANGES-1.14.txt
- https://github.com/advisories/GHSA-j8g6-2wh7-6439
- https://github.com/apache/tika
- https://lists.apache.org/thread.html/91eb639ef619b9a26b40020ca6732e7dbe457f7322ed5f1df49e411a@%3Cdev.nutch.apache.org%3E
- https://lists.apache.org/thread.html/d2375da29d89e679abf5d845db76d6f798fdc6f7d44f2c788e8a0fb9@%3Cuser.nutch.apache.org%3E
- https://lists.apache.org/thread.html/e414754a6c57ce7194b731e211cd6b2cbb41f2c7000e3fb9c6b6ec78@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/r2f6f6c130b12b7332f323f74d031072b1517065ce28a22346791ffb6@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/rfd3646bb724b66b1a9ddef69e692da2b7a727a8799551c78eedf0a0f@%3Cissues.lucene.apache.org%3E
- http://seclists.org/bugtraq/2016/Nov/40
- http://www.securityfocus.com/bid/94247
