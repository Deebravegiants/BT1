# [M] Apache Airflow's create action can upsert existing Pools/Connections/Variables

## Summary
Severity: Medium
Advisory: GHSA-gp5f-cx7h-8q6f
CVE: CVE-2025-62503
CWE: CWE-250
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-gp5f-cx7h-8q6f
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.1.1

## Details
User with CREATE and no UPDATE privilege for Pools, Connections, Variables could update existing records via bulk create API with overwrite action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62503
- https://github.com/apache/airflow
- https://lists.apache.org/thread/ov923dyccwbv01v9mhcv7t7ykzobycfo
- http://www.openwall.com/lists/oss-security/2025/10/29/8
