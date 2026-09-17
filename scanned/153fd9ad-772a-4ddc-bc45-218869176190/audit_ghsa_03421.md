# [C] Authentication bypass in Apache Airflow

## Summary
Severity: Critical
Advisory: GHSA-hhx9-p69v-cx2j
CVE: CVE-2020-13927
CWE: CWE-1056, CWE-1188, CWE-287, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-hhx9-p69v-cx2j
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.11

## Details
The previous default setting for Airflow's Experimental API was to allow all API requests without authentication, but this poses security risks to users who miss this fact. From Airflow 1.10.11 the default has been changed to deny all requests by default and is documented at https://airflow.apache.org/docs/1.10.11/security.html#api-authentication. Note this change fixes it for new installs but existing users need to change their config to default `[api]auth_backend = airflow.api.auth.backend.deny_all` as mentioned in the Updating Guide: https://github.com/apache/airflow/blob/1.10.11/UPDATING.md#experimental-api-will-deny-all-request-by-default

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13927
- https://github.com/apache/airflow/pull/9611
- https://github.com/apache/airflow/commit/180bca4f993b7b778a8d2c65d3d357652218922b
- https://github.com/apache/airflow/commit/9e305d6b810a2a21e2591a80a80ec41acb3afed0
- https://airflow.apache.org/docs/apache-airflow/1.10.11/security.html#api-authentication
- https://github.com/advisories/GHSA-hhx9-p69v-cx2j
- https://github.com/apache/airflow
- https://github.com/apache/airflow/releases/tag/1.10.11
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-18.yaml
- https://lists.apache.org/thread.html/r23a81b247aa346ff193670be565b2b8ea4b17ddbc7a35fc099c1aadd%40%3Cdev.airflow.apache.org%3E
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-13927
- http://packetstormsecurity.com/files/162908/Apache-Airflow-1.10.10-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/174764/Apache-Airflow-1.10.10-Remote-Code-Execution.html
