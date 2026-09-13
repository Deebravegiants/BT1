# [M] Moderate severity vulnerability that affects com.sparkjava:spark-core

## Summary
Severity: Medium
Advisory: GHSA-76qr-mmh8-cp8f
CVE: CVE-2018-9159
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-76qr-mmh8-cp8f
Type: github-advisory

## Affected
- Maven: `com.sparkjava:spark-core` — affected >=0 <2.7.2

## Details
In Spark before 2.7.2, a remote attacker can read unintended static files via various representations of absolute or relative pathnames, as demonstrated by file: URLs and directory traversal sequences. NOTE: this product is unrelated to Ignite Realtime Spark.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9159
- https://github.com/perwendel/spark/issues/981
- https://github.com/perwendel/spark/commit/030e9d00125cbd1ad759668f85488aba1019c668
- https://github.com/perwendel/spark/commit/a221a864db28eb736d36041df2fa6eb8839fc5cd
- https://github.com/perwendel/spark/commit/ce9e11517eca69e58ed4378d1e47a02bd06863cc
- https://access.redhat.com/errata/RHSA-2018:2020
- https://access.redhat.com/errata/RHSA-2018:2405
- https://github.com/advisories/GHSA-76qr-mmh8-cp8f
- https://github.com/perwendel/spark
- http://sparkjava.com/news#spark-272-released
