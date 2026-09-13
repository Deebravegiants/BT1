# [H] Authentication Bypass by Capture-replay in Apache Spark

## Summary
Severity: High
Advisory: GHSA-9rr6-jpg7-9jg6
CVE: CVE-2021-38296
CWE: CWE-294
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-9rr6-jpg7-9jg6
Type: github-advisory

## Affected
- Maven: `org.apache.spark:spark-core` — affected >=0 <3.1.3
- PyPI: `pyspark` — affected >=0 <3.1.3

## Details
Apache Spark supports end-to-end encryption of RPC connections via "spark.authenticate" and "spark.network.crypto.enabled". In versions 3.1.2 and earlier, it uses a bespoke mutual authentication protocol that allows for full encryption key recovery. After an initial interactive attack, this would allow someone to decrypt plaintext traffic offline. Note that this does not affect security mechanisms controlled by "spark.authenticate.enableSaslEncryption", "spark.io.encryption.enabled", "spark.ssl", "spark.ui.strictTransportSecurity". Update to Apache Spark 3.1.3 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38296
- https://github.com/advisories/GHSA-9rr6-jpg7-9jg6
- https://github.com/pypa/advisory-database/tree/main/vulns/pyspark/PYSEC-2022-186.yaml
- https://lists.apache.org/thread/70x8fw2gx3g9ty7yk0f2f1dlpqml2smd
- https://www.oracle.com/security-alerts/cpujul2022.html
