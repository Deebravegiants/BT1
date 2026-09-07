# [M] Exposure of Sensitive Information to an Unauthorized Actor in Apache Spark via crafted URL

## Summary
Severity: Medium
Advisory: GHSA-8cw6-5qvp-q3wj
CVE: CVE-2018-8024
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-03-14
Source: https://github.com/advisories/GHSA-8cw6-5qvp-q3wj
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.10` — affected >=2.1.0 <2.1.3
- Maven: `org.apache.spark:spark-core_2.10` — affected >=2.2.0 <2.2.2
- Maven: `org.apache.spark:spark-core_2.11` — affected >=2.1.0 <2.1.3
- Maven: `org.apache.spark:spark-core_2.11` — affected >=2.2.0 <2.2.2
- Maven: `org.apache.spark:spark-core_2.11` — affected >=2.3.0 <2.3.1

## Details
In Apache Spark 2.1.0 to 2.1.2, 2.2.0 to 2.2.1, and 2.3.0, it's possible  for a malicious user to construct a URL pointing to a Spark cluster's UI's  job and stage info pages, and if a user can be tricked into accessing  the URL, can be used to cause script to execute and expose information  from the user's view of the Spark UI. While some browsers like recent  versions of Chrome and Safari are able to block this type of attack,  current versions of Firefox (and possibly others) do not.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8024
- https://github.com/advisories/GHSA-8cw6-5qvp-q3wj
- https://lists.apache.org/thread.html/5f241d2cda21cbcb3b63e46e474cf5f50cce66927f08399f4fab0aba@%3Cdev.spark.apache.org%3E
- https://spark.apache.org/security.html#CVE-2018-8024
