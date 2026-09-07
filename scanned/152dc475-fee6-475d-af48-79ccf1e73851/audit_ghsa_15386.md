# [M] Apache Airflow Cross-site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w7cp-g8v7-r54m
CVE: CVE-2024-41937
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-21
Source: https://github.com/advisories/GHSA-w7cp-g8v7-r54m
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.10.0

## Details
Apache Airflow, versions before 2.10.0, have a vulnerability that allows the developer of a malicious provider to execute a cross-site scripting attack when clicking on a provider documentation link. This would require the provider to be installed on the web server and the user to click the provider link.
Users should upgrade to 2.10.0 or later, which fixes this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-41937
- https://github.com/apache/airflow/pull/40933
- https://github.com/apache/airflow/commit/f1852c2ab28b155e196569780013fbb61a4a1f98
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-181.yaml
- https://lists.apache.org/thread/lwlmgg6hqfmkpvw5py4w53hxyl37jl6d
- http://www.openwall.com/lists/oss-security/2024/08/21/3
