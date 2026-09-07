# [M] Apache Airflow Reflected Cross-site Scripting vulnerability in 404 Endpoint

## Summary
Severity: Medium
Advisory: GHSA-rv25-9wgj-xg75
CVE: CVE-2017-12614
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rv25-9wgj-xg75
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.9.0

## Details
It was noticed an XSS in certain 404 pages that could be exploited to perform an XSS attack. Chrome will detect this as a reflected XSS attempt and prevent the page from loading. However Firefox and other browsers don't, and are vulnerable to this attack. Mitigation: The fix for this is to upgrade to Apache Airflow 1.9.0 or above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12614
- https://github.com/apache/airflow/commit/e1a2d74c0045c9231f7a5365c956b8e048dd6af3
- https://devhub.checkmarx.com/cve-details/cve-2017-12614
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2018-45.yaml
- https://lists.apache.org/thread.html/2c72480c76619c5e7793f0d213c34082f0598eaa4d212172f068940f@%3Cdev.airflow.apache.org%3E
