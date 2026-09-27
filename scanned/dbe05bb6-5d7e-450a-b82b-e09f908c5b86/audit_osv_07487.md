# [C] BIT-spark-2020-9480

## Summary
Severity: Critical
Advisory: BIT-spark-2020-9480
Aliases: CVE-2020-9480, GHSA-wgx7-jwwm-cgjv, PYSEC-2020-95
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-spark-2020-9480
Type: osv

## Affected
- Bitnami: `spark` — affected >=0 <2.4.6

## Details
In Apache Spark 2.4.5 and earlier, a standalone resource manager's master may be configured to require authentication (spark.authenticate) via a shared secret. When enabled, however, a specially-crafted RPC to the master can succeed in starting an application's resources on the Spark cluster, even without the shared key. This can be leveraged to execute shell commands on the host machine. This does not affect Spark clusters using other resource managers (YARN, Mesos, etc).

## References
- https://lists.apache.org/thread.html/r03ad9fe7c07d6039fba9f2152d345274473cb0af3d8a4794a6645f4b%40%3Cuser.spark.apache.org%3E
- https://lists.apache.org/thread.html/ra0e62a18ad080c4ce6df5e0202a27eaada75222761efc3f7238b5a3b%40%3Ccommits.doris.apache.org%3E
- https://lists.apache.org/thread.html/rb3956440747e41940d552d377d50b144b60085e7ff727adb0e575d8d%40%3Ccommits.submarine.apache.org%3E
- https://lists.apache.org/thread.html/ree9e87aae81852330290a478692e36ea6db47a52a694545c7d66e3e2%40%3Cdev.spark.apache.org%3E
- https://spark.apache.org/security.html#CVE-2020-9480
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-9480
