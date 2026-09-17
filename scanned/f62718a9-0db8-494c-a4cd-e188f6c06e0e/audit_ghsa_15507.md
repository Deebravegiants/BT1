# [H] Apache Airflow vulnerable to Improper Encoding or Escaping of Output

## Summary
Severity: High
Advisory: GHSA-c392-whpc-vfpr
CVE: CVE-2024-45498
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-07
Source: https://github.com/advisories/GHSA-c392-whpc-vfpr
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.10.0 <2.10.1

## Details
Example DAG: example_inlet_event_extra.py shipped with Apache Airflow version 2.10.0 has a vulnerability that allows an authenticated attacker with only DAG trigger permission to execute arbitrary commands. If you used that example as the base of your DAGs - please review if you have not copied the dangerous example; see  https://github.com/apache/airflow/pull/41873  for more information. We recommend against exposing the example DAGs in your deployment. If you must expose the example DAGs, upgrade Airflow to version 2.10.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45498
- https://github.com/apache/airflow/pull/41873
- https://github.com/apache/airflow/commit/09ec2616568f8a18e0d5fe408110fae06ddf748f
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-266.yaml
- https://lists.apache.org/thread/tl7lzczcqdmqj2pcpbvtjdpd2tb9561n
- https://www.openwall.com/lists/oss-security/2024/09/06/2
- http://www.openwall.com/lists/oss-security/2024/09/06/2
