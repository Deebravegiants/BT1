# [H] CVE-2018-1296

## Summary
Severity: High
Advisory: CVE-2018-1296
Aliases: GHSA-v569-g72v-q434
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-02-07
Source: https://osv.dev/vulnerability/CVE-2018-1296
Type: osv

## Details
In Apache Hadoop 3.0.0-alpha1 to 3.0.0, 2.9.0, 2.8.0 to 2.8.3, and 2.5.0 to 2.7.5, HDFS exposes extended attribute key/value pairs during listXAttrs, verifying only path-level search access to the directory rather than path-level read permission to the referent.

## References
- https://lists.apache.org/thread.html/a5b15bc76fbdad2ee40761aacf954a13aeef67e305f86d483f267e8e%40%3Cuser.hadoop.apache.org%3E
- http://www.securityfocus.com/bid/106764
