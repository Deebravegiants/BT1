# [M] Users can view database names in Apache Superset

## Summary
Severity: Medium
Advisory: GHSA-9c29-9h4m-wg5p
CVE: CVE-2019-12414
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-02-26
Source: https://github.com/advisories/GHSA-9c29-9h4m-wg5p
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <0.32.0

## Details
In Apache Incubator Superset before 0.32, a user can view database names that he has no access to on a dropdown list in SQLLab

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12414
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2019-173.yaml
- https://lists.apache.org/thread.html/396034aabe08dd349ff44eb062c718aadcf1b4e86f6372c7d5e988c0%40%3Cdev.superset.apache.org%3E
