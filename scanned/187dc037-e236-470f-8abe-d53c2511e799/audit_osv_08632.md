# [M] CVE-2016-5001

## Summary
Severity: Medium
Advisory: CVE-2016-5001
Aliases: GHSA-8r28-r8cp-g6cp
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2016-5001
Type: osv

## Details
This is an information disclosure vulnerability in Apache Hadoop before 2.6.4 and 2.7.x before 2.7.2 in the short-circuit reads feature of HDFS. A local user on an HDFS DataNode may be able to craft a block token that grants unauthorized read access to random files by guessing certain fields in the token.

## References
- https://lists.apache.org/thread.html/r66de86b9a608c1da70b2d27d765c11ec88edf6e5dd6f379ab33e072a%40%3Cuser.flink.apache.org%3E
- http://seclists.org/oss-sec/2016/q4/698
- http://www.securityfocus.com/bid/94950
