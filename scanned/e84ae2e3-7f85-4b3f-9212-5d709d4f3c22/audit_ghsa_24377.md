# [H] Improper Access Control in Apache Hadoop

## Summary
Severity: High
Advisory: GHSA-7q56-mp4c-gggg
CVE: CVE-2016-5393
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7q56-mp4c-gggg
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-common` — affected >=2.6.0 <2.6.5
- Maven: `org.apache.hadoop:hadoop-common` — affected >=2.7.0 <2.7.3

## Details
In Apache Hadoop 2.6.x before 2.6.5 and 2.7.x before 2.7.3, a remote user who can authenticate with the HDFS NameNode can possibly run arbitrary commands with the same privileges as the HDFS service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5393
- http://mail-archives.apache.org/mod_mbox/hadoop-general/201611.mbox/%3CCAA0W1bTbUmUUSF1rjRpX-2DvWutcrPt7TJSWUcSLg1F0gyHG1Q%40mail.gmail.com%3E
- http://www.securityfocus.com/bid/94574
