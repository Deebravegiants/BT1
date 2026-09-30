# [H] Apache IoTDB subject to ReDOS with Java 8

## Summary
Severity: High
Advisory: GHSA-g6hg-4v3c-6jq7
CVE: CVE-2022-43766
CWE: CWE-400
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-g6hg-4v3c-6jq7
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:flink-tsfile-connector` — affected >=0.12.2 <0.13.3
- PyPI: `apache-iotdb` — affected >=0.12.2 <0.13.3
- Maven: `org.apache.iotdb:iotdb-server` — affected >=0.12.2 <0.13.3
- Maven: `org.apache.iotdb:tsfile` — affected >=0.12.2 <0.13.3

## Details
Apache IoTDB versions 0.12.2 through 0.12.6, and 0.13.0 through 0.13.2 are vulnerable to a Denial of Service attack when accepting untrusted patterns for REGEXP queries with Java 8. This issue is patched in 0.13.3. Users should upgrade or use a later version of Java to avoid it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43766
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2022-42972.yaml
- https://lists.apache.org/thread/9pgpb82p5brooy41n8l5q0y9h33db2zn
