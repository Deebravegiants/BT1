# [H] Apache Airflow providers-google's `ComputeEngineSSHHook` disables SSH host-key verification by default

## Summary
Severity: High
Advisory: GHSA-g9v5-gjwf-9rwx
CVE: CVE-2026-45361
CWE: CWE-322
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-g9v5-gjwf-9rwx
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-google` — affected >=0 <22.0.0

## Details
Apache Airflow providers-google's `ComputeEngineSSHHook` disables SSH host-key verification by default, exposing SSH traffic between an Airflow worker and a Compute Engine VM to in-path network attackers who can intercept or modify the session. Users are advised to upgrade to `apache-airflow-providers-google` 22.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45361
- https://github.com/apache/airflow/pull/66746
- https://github.com/apache/airflow/commit/120dbed3462cedcb980aac022c587ba434249eb1
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow-providers-google/PYSEC-2026-166.yaml
- https://lists.apache.org/thread/3lpj7ppwxp7jtp81rnxk75xvln7qd7h2
- http://www.openwall.com/lists/oss-security/2026/05/24/9
