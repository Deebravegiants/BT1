# [M] Apache Airflow has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-f6vj-48fm-hmvx
CVE: CVE-2026-49818
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-f6vj-48fm-hmvx
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-samba` — affected >=0 <4.12.6

## Details
The Apache Airflow Samba provider's `GCSToSambaOperator` joined GCS object names to the SMB destination path without a containment check, so an object named with `../` segments resolved a write path outside the configured `destination_path`. An attacker able to write objects into the source GCS bucket — typically an external data producer distinct from the trusted DAG author — could write files to arbitrary locations on the Samba target when the operator ran. Upgrade apache-airflow-providers-samba to 4.12.6 or later, which validates the resolved destination stays within `destination_path`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-49818
- https://github.com/apache/airflow/pull/67857
- https://github.com/apache/airflow/commit/bc1df029af15cb1d35d5ca0d33bf9235500137cc
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-samba/PYSEC-2026-208.yaml
- https://lists.apache.org/thread/3vs0m3p51psgf54tts18d6336g24x3sf
- http://www.openwall.com/lists/oss-security/2026/06/09/8
