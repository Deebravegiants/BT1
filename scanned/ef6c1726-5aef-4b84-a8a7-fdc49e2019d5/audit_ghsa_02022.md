# [M] Apache Airflow Cross-site Scripting 

## Summary
Severity: Medium
Advisory: GHSA-4pwq-fj89-6rjc
CVE: CVE-2020-13944
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-4pwq-fj89-6rjc
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.12

## Details
In Apache Airflow < 1.10.12, the `origin` parameter passed to some of the endpoints like `/trigger` and was vulnerable to a XSS exploit.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13944
- https://github.com/apache/airflow/commit/5c2bb7b0b0e717b11f093910b443243330ad93ca
- https://github.com/advisories/GHSA-4pwq-fj89-6rjc
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-19.yaml
- https://lists.apache.org/thread.html/r2892ef594dbbf54d0939b808626f52f7c2d1584f8aa1d81570847d2a@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r2892ef594dbbf54d0939b808626f52f7c2d1584f8aa1d81570847d2a@%3Cdev.airflow.apache.org%3E
- https://lists.apache.org/thread.html/r2892ef594dbbf54d0939b808626f52f7c2d1584f8aa1d81570847d2a@%3Cusers.airflow.apache.org%3E
- https://lists.apache.org/thread.html/r4656959c8ed06c1f6202d89aa4e67b35ad7bdba5a666caff3fea888e@%3Cusers.airflow.apache.org%3E
- https://lists.apache.org/thread.html/r97e1b60ca508a86be58c43f405c0c8ff00ba467ba0bee68704ae7e3e%40%3Cdev.airflow.apache.org%3E
- https://lists.apache.org/thread.html/ra8ce70088ba291f358e077cafdb14d174b7a1ce9a9d86d1b332d6367@%3Cusers.airflow.apache.org%3E
- https://lists.apache.org/thread.html/rc005f4de9d9b0ba943ceb8ff5a21a5c6ff8a9df52632476698d99432@%3Cannounce.apache.org%3E
- http://www.openwall.com/lists/oss-security/2020/12/11/2
- http://www.openwall.com/lists/oss-security/2021/05/01/2
