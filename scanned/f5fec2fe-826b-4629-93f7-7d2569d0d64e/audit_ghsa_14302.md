# [C] Apache IoTDB Grafana Connector vulnerable to Improper Authentication

## Summary
Severity: Critical
Advisory: GHSA-pvjv-386f-c8wh
CVE: CVE-2023-24831
CWE: CWE-287
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-17
Source: https://github.com/advisories/GHSA-pvjv-386f-c8wh
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-grafana-connector` — affected >=0.13.0 <0.13.4
- PyPI: `apache-iotdb` — affected >=0.13.0 <0.13.5

## Details
Improper Authentication vulnerability in Apache Software Foundation Apache IoTDB. This issue affects Apache IoTDB Grafana Connector from 0.13.0 through 0.13.3.

Attackers could log in without authorization. This is fixed in 0.13.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24831
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2023-7.yaml
- https://lists.apache.org/thread/3dgvzgstycf8b5hyf4z3n7cqdhcyln3l
