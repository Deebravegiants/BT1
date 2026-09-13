# [H] Apache IoTDB: Denial of Service via Resource Exhaustion in Aggregation Query

## Summary
Severity: High
Advisory: CVE-2026-24012
Aliases: PYSEC-2026-2079
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-24012
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in Apache IoTDB. 

Some interface fails to impose reasonable
limits on the time span and aggregation interval of the query. An attacker
can construct a request with extreme parameters (e.g., a very large time
range combined with a minimal interval). This forces the DataNode to build
an enormous result set in memory, which exhausts the Java heap and causes
the DataNode process to crash.

This issue affects Apache IoTDB: from 1.3.3 before 2.0.8.

Users are recommended to upgrade to version 2.0.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24012.json
- https://lists.apache.org/thread/0g5th1t2vj6j8hm5t9w3xh9n6f6ht9z8
- https://nvd.nist.gov/vuln/detail/CVE-2026-24012
