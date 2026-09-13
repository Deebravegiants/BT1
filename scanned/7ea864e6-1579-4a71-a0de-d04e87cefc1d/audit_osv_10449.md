# [M] CVE-2017-15713

## Summary
Severity: Medium
Advisory: CVE-2017-15713
Aliases: GHSA-3v44-382q-55f4
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-19
Source: https://osv.dev/vulnerability/CVE-2017-15713
Type: osv

## Details
Vulnerability in Apache Hadoop 0.23.x, 2.x before 2.7.5, 2.8.x before 2.8.3, and 3.0.0-alpha through 3.0.0-beta1 allows a cluster user to expose private files owned by the user running the MapReduce job history server process. The malicious user can construct a configuration file containing XML directives that reference sensitive files on the MapReduce job history server host.

## References
- https://lists.apache.org/thread.html/a790a251ace7213bde9f69777dedb453b1a01a6d18289c14a61d4f91%40%3Cgeneral.hadoop.apache.org%3E
