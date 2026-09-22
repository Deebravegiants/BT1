# [H] Sensitive data written to disk unencrypted in Spark

## Summary
Severity: High
Advisory: GHSA-fp5j-3fpf-mhj5
CVE: CVE-2019-10099
CWE: CWE-312
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-08-08
Source: https://github.com/advisories/GHSA-fp5j-3fpf-mhj5
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.11` — affected >=0 <2.3.3
- PyPI: `pyspark` — affected >=0 <2.3.3

## Details
Prior to Spark 2.3.3, in certain situations Spark would write user data to local disk unencrypted, even if spark.io.encryption.enabled=true. This includes cached blocks that are fetched to disk (controlled by spark.maxRemoteBlockSizeFetchToMem); in SparkR, using parallelize; in Pyspark, using broadcast and parallelize; and use of python udfs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10099
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2019-114.yaml
- https://lists.apache.org/thread.html/c2a39c207421797f82823a8aff488dcd332d9544038307bf69a2ba9e@%3Cuser.spark.apache.org%3E
- https://lists.apache.org/thread.html/ra216b7b0dd82a2c12c2df9d6095e689eb3f3d28164e6b6587da69fae@%3Ccommits.spark.apache.org%3E
- https://lists.apache.org/thread.html/rabe1d47e2bf8b8f6d9f3068c8d2679731d57fa73b3a7ed1fa82406d2@%3Cissues.spark.apache.org%3E
