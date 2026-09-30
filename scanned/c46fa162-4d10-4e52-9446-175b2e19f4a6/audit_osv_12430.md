# [H] CVE-2018-11804

## Summary
Severity: High
Advisory: CVE-2018-11804
Aliases: GHSA-62g2-m955-v383
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-24
Source: https://osv.dev/vulnerability/CVE-2018-11804
Type: osv

## Details
Spark's Apache Maven-based build includes a convenience script, 'build/mvn', that downloads and runs a zinc server to speed up compilation. It has been included in release branches since 1.3.x, up to and including master. This server will accept connections from external hosts by default. A specially-crafted request to the zinc server could cause it to reveal information in files readable to the developer account running the build. Note that this issue does not affect end users of Spark, only developers building Spark from source code.

## References
- http://www.securityfocus.com/bid/105756
- https://lists.apache.org/thread.html/2b11aa4201e36f2ec8f728e722fe33758410f07784379cbefd0bda9d%40%3Cdev.spark.apache.org%3E
- https://spark.apache.org/security.html#CVE-2018-11804
