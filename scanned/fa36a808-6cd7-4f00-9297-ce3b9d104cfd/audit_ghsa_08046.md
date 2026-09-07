# [H] Apache Airflow vulnerable to Code Injection in the web-server context via LogTemplate table

## Summary
Severity: High
Advisory: GHSA-r837-hpv7-pc2f
CVE: CVE-2024-56373
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-r837-hpv7-pc2f
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.11.1

## Details
DAG Author (who already has quite a lot of permissions) could manipulate database of Airflow 2 in the way to execute arbitrary code in the web-server context, which they should normally not be able to do, leading to potentially remote code execution in the context of web-server (server-side) as a result of a user viewing historical task information.

The functionality responsible for that (log template history) has been disabled by default in 2.11.1 and users should upgrade to Airflow 3 if they want to continue to use log template history. They can also manually modify historical log file names if they want to see historical logs that were generated before the last log template change.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-56373
- https://github.com/apache/airflow/pull/61880
- https://github.com/apache/airflow
- https://lists.apache.org/thread/2vrmrhcht6g7cp5yjxpnrk2wtrncm6cy
- http://www.openwall.com/lists/oss-security/2026/02/23/3
