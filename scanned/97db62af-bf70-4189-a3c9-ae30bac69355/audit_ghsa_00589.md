# [C] Remote Code Execution in spark-core

## Summary
Severity: Critical
Advisory: GHSA-phg2-9c5g-m4q7
CVE: CVE-2018-17190
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-phg2-9c5g-m4q7
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.11` — affected >=0
- Maven: `org.apache.spark:spark-core_2.10` — affected >=0

## Details
In all versions of Apache Spark, its standalone resource manager accepts code to execute on a 'master' host, that then runs that code on 'worker' hosts. The master itself does not, by design, execute user code. A specially-crafted request to the master can, however, cause the master to execute code too. Note that this does not affect standalone clusters with authentication enabled. While the master host typically has less outbound access to other resources than a worker, the execution of code on the master is nevertheless unexpected.

# Mitigation
Enable authentication on any Spark standalone cluster that is not otherwise secured from unwanted access, for example by network-level restrictions. Use spark.authenticate and related security properties described at https://spark.apache.org/docs/latest/security.html

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17190
- https://github.com/advisories/GHSA-phg2-9c5g-m4q7
- https://lists.apache.org/thread.html/341c3187f15cdb0d353261d2bfecf2324d56cb7db1339bfc7b30f6e5@%3Cdev.spark.apache.org%3E
- https://security.gentoo.org/glsa/201903-21
- https://www.oracle.com/security-alerts/cpujul2020.html
- http://www.securityfocus.com/bid/105976
