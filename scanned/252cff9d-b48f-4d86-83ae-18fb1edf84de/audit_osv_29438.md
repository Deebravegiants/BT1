# [C] Apache Airflow Providers FAB: FAB provider 1.2.1 and 1.2.0 did not let user to logout for Airflow

## Summary
Severity: Critical
Advisory: CVE-2024-42447
Aliases: GHSA-62qf-qm3g-fvcw, PYSEC-2024-265, PYSEC-2026-1146
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-05
Source: https://osv.dev/vulnerability/CVE-2024-42447
Type: osv

## Details
Insufficient Session Expiration vulnerability in Apache Airflow Providers FAB.

This issue affects Apache Airflow Providers FAB: 1.2.1 (when used with Apache Airflow 2.9.3) and FAB 1.2.0 for all Airflow versions. The FAB provider prevented the user from logging out.  

* FAB provider 1.2.1 only affected Airflow 2.9.3 (earlier and later versions of Airflow are not affected)

* FAB provider 1.2.0 affected all versions of Airflow.

Users who run Apache Airflow 2.9.3 are recommended to upgrade to Apache Airflow Providers FAB version 1.2.2 which fixes the issue.

Users who run Any Apache Airflow version and have FAB provider 1.2.0 are recommended to upgrade to Apache Airflow Providers FAB version 1.2.2 which fixes the issue.

Also upgrading Apache Airflow to latest version available is recommended.

Note: Early version of Airflow reference container images of Airflow 2.9.3 and constraint files contained FAB provider 1.2.1 version, but this is fixed in updated versions of the images. 

Users are advised to pull the latest Airflow images or reinstall FAB provider according to the current constraints.

## References
- http://www.openwall.com/lists/oss-security/2024/08/04/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42447.json
- https://lists.apache.org/thread/2zoo8cjlwfjhbfdxfgltcm0hnc0qmc52
- https://nvd.nist.gov/vuln/detail/CVE-2024-42447
- https://github.com/apache/airflow/pull/40784
- https://pypi.org/project/apache-airflow-providers-fab/
