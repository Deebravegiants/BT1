# [H] Arbitrary Command Execution in Hadoop

## Summary
Severity: High
Advisory: GHSA-rqj9-cq6j-958r
CVE: CVE-2018-11766
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-rqj9-cq6j-958r
Type: github-advisory

## Affected
- Maven: `org.apache.hadoop:hadoop-main` — affected >=2.7.4 <2.7.7

## Details
In Apache Hadoop 2.7.4 to 2.7.6, the security fix for CVE-2016-6811 is incomplete. A user who can escalate to yarn user can possibly run arbitrary commands as root user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11766
- https://github.com/advisories/GHSA-rqj9-cq6j-958r
- https://lists.apache.org/thread.html/ff37bbbe09d5f03090e2dd2c3dea95de16ef4249e731f19b8959ce4c@%3Cgeneral.hadoop.apache.org%3E
- http://www.securityfocus.com/bid/106035
