# [C] Missing Authentication for Critical Function in Apache Airflow

## Summary
Severity: Critical
Advisory: GHSA-h88f-r7cw-8fv3
CVE: CVE-2021-38540
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h88f-r7cw-8fv3
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.0.0 <2.1.3

## Details
The variable import endpoint was not protected by authentication in Airflow >=2.0.0, <2.1.3. This allowed unauthenticated users to hit that endpoint to add/modify Airflow variables used in DAGs, potentially resulting in a denial of service, information disclosure or remote code execution. This issue affects Apache Airflow >=2.0.0, <2.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38540
- https://github.com/apache/airflow/commit/bcec1df703cd4a01520a90c3f801cca6f97d9bfd
- https://github.com/advisories/GHSA-h88f-r7cw-8fv3
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2021-326.yaml
- https://lists.apache.org/thread.html/rac2ed9118f64733e47b4f1e82ddc8c8020774698f13328ca742b03a2@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rb34c3dd1a815456355217eef34060789f771b6f77c3a3dec77de2064%40%3Cusers.airflow.apache.org%3E
