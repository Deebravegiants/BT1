# [M] CVE-2019-0226

## Summary
Severity: Medium
Advisory: CVE-2019-0226
Aliases: GHSA-fjw4-39pg-vf4f
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2019-0226
Type: osv

## Details
Apache Karaf Config service provides a install method (via service or MBean) that could be used to travel in any directory and overwrite existing file. The vulnerability is low if the Karaf process user has limited permission on the filesystem. Any Apache Karaf version before 4.2.5 is impacted. User should upgrade to Apache Karaf 4.2.5 or later.

## References
- https://lists.apache.org/thread.html/1baa6f1df0e95fb1cd679067117354af2ab4423277d9a0ff6e8bf790%40%3Cdev.karaf.apache.org%3E
- https://lists.apache.org/thread.html/r218c7e017af0a860ae21bf7ab77520fd2070c8f52db680eeec03a266%40%3Ccommits.karaf.apache.org%3E
