# [H] Apache Spark Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-8rhc-48pp-52gr
CVE: CVE-2017-12612
CWE: CWE-502
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-8rhc-48pp-52gr
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.11` — affected >=0 <2.1.2
- Maven: `org.apache.spark:spark-core_2.10` — affected >=0 <2.1.2
- PyPI: `pyspark` — affected >=0 <2.1.2

## Details
In Apache Spark 1.6.0 until 2.1.1, the launcher API performs unsafe deserialization of data received by its socket. This makes applications launched programmatically using the launcher API potentially vulnerable to arbitrary code execution by an attacker with access to any user account on the local machine. It does not affect apps run by spark-submit or spark-shell. The attacker would be able to execute code as the user that ran the Spark application. Users are encouraged to update to version 2.1.2, 2.2.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12612
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2017-147.yaml
- https://mail-archives.apache.org/mod_mbox/spark-dev/201709.mbox/%3CCAEccTyy-1yYuhdNgkBUg0sr9NeaZSrBKkBePdTNZbxXZNTAR-g%40mail.gmail.com%3E
