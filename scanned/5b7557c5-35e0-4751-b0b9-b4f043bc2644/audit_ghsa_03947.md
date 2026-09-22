# [M] Pyspark User Impersonation Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fvxv-9xxr-h7wj
CVE: CVE-2018-11760
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-fvxv-9xxr-h7wj
Type: github-advisory

## Affected
- PyPI: `pyspark` — affected >=2.3.0 <2.3.2
- PyPI: `pyspark` — affected >=1.0.2 <2.2.3

## Details
When using PySpark , it's possible for a different local user to connect to the Spark application and impersonate the user running the Spark application. This affects versions 1.x, 2.0.x, 2.1.x, 2.2.0 to 2.2.2, and 2.3.0 to 2.3.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11760
- https://github.com/advisories/GHSA-fvxv-9xxr-h7wj
- https://github.com/apache/spark
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2019-169.yaml
- https://lists.apache.org/thread.html/6d015e56b3a3da968f86e0b6acc69f17ecc16b499389e12d8255bf6e@%3Ccommits.spark.apache.org%3E
- https://lists.apache.org/thread.html/a86ee93d07b6f61b82b61a28049aed311f5cc9420d26cc95f1a9de7b@%3Cuser.spark.apache.org%3E
- https://web.archive.org/web/20200227091119/http://www.securityfocus.com/bid/106786
- https://web.archive.org/web/20200925111106/https://issues.apache.org/jira/browse/SPARK-26802
