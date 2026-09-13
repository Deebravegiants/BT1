# [M] Apache Airflow Has an Authorization Bypass That Allows Unauthorized Task Log Access

## Summary
Severity: Medium
Advisory: GHSA-pm44-x5x7-24c4
CVE: CVE-2026-22922
CWE: CWE-648
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-pm44-x5x7-24c4
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.1.0 <3.1.7

## Details
## Vulnerability Overview

An authorization bypass vulnerability exists in Apache Airflow that allows authenticated users to access task execution logs without the required permissions.

## The Flaw

The vulnerability affects environments using custom roles or granular permission settings. Normally, Airflow allows administrators to separate "Task" access (viewing the task state) from "Task Log" access (viewing the console output/logs).

In affected versions, the permission check for retrieving logs is insufficient. An authenticated user who has been granted access to view Tasks can successfully request and view Task Logs, even if they do not have the specific `can_read` permission for Logs.

## Impact

- **Confidentiality Loss:** Task logs often contain sensitive operational data, debugging information, or potentially leaked secrets (environment variables, connection strings) that should not be visible to all users with basic task access.
- **Broken Access Control:** This bypasses the intended security model for restricted user roles.

## Affected Versions

- Apache Airflow 3.1.0 through 3.1.6

## Patches

Users should upgrade to Apache Airflow **3.1.7** or later, which enforces the correct permission checks for log access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22922
- https://github.com/apache/airflow/pull/60412
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-11.yaml
- https://lists.apache.org/thread/gdb7vffhpmrj5hp1j0oj1j13o4vmsq40
- http://www.openwall.com/lists/oss-security/2026/02/09/2
