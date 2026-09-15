# [M] CVE-2018-1334

## Summary
Severity: Medium
Advisory: CVE-2018-1334
Aliases: GHSA-6mqq-8r44-vmjc, PYSEC-2018-25
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-12
Source: https://osv.dev/vulnerability/CVE-2018-1334
Type: osv

## Details
In Apache Spark 1.0.0 to 2.1.2, 2.2.0 to 2.2.1, and 2.3.0, when using PySpark or SparkR, it's possible for a different local user to connect to the Spark application and impersonate the user running the Spark application.

## References
- https://lists.apache.org/thread.html/4d6d210e319a501b740293daaeeeadb51927111fb8261a3e4cd60060%40%3Cdev.spark.apache.org%3E
- https://spark.apache.org/security.html#CVE-2018-1334
