# [M] org.apache.spark:spark-core_2.10 and org.apache.spark:spark-core_2.11 Improper Authentication vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w4r4-65mg-45x2
CVE: CVE-2018-11770
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-w4r4-65mg-45x2
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core_2.11` — affected >=1.0.0
- Maven: `org.apache.spark:spark-core_2.10` — affected >=1.0.0

## Details
From version 1.3.0 onward, Apache Spark's standalone master exposes a REST API for job submission, in addition to the submission mechanism used by spark-submit. In standalone, the config property 'spark.authenticate.secret' establishes a shared secret for authenticating requests to submit jobs via spark-submit. However, the REST API does not use this or any other authentication mechanism, and this is not adequately documented. In this case, a user would be able to run a driver program without authenticating, but not launch executors, using the REST API. This REST API is also used by Mesos, when set up to run in cluster mode (i.e., when also running MesosClusterDispatcher), for job submission. Future versions of Spark will improve documentation on these points, and prohibit setting 'spark.authenticate.secret' when running the REST APIs, to make this clear. Future 2.4.x versions will also disable the REST API by default in the standalone master by changing the default value of 'spark.master.rest.enabled' to 'false'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11770
- https://lists.apache.org/thread.html/bd8e51314041451a2acd720e9223fc1c15a263ccacb396a75b1fc485%40%3Cdev.spark.apache.org%3E
- https://lists.apache.org/thread.html/bd8e51314041451a2acd720e9223fc1c15a263ccacb396a75b1fc485@%3Cdev.spark.apache.org%3E
- https://spark.apache.org/security.html#CVE-2018-11770
- https://web.archive.org/web/20200227114942/http://www.securityfocus.com/bid/105097
