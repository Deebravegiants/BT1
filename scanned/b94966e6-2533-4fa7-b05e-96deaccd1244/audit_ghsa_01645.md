# [M] Users able to query database metadata in Apache Superset

## Summary
Severity: Medium
Advisory: GHSA-p5w7-qmq6-pmjr
CVE: CVE-2019-12413
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-02-26
Source: https://github.com/advisories/GHSA-p5w7-qmq6-pmjr
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <0.31.0

## Details
In Apache Incubator Superset before 0.31 user could query database metadata information from a database he has no access to, by using a specially crafted complex query.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12413
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2019-172.yaml
- https://lists.apache.org/thread.html/85ab04f8c52df8c353ecfa0ecd2ff27fc07fb8ab7566a754349806be%40%3Cdev.superset.apache.org%3E
- https://snyk.io/vuln/SNYK-PYTHON-APACHESUPERSET-558911
