# [H] Remote code execution in Apache Airflow Docker's Provider

## Summary
Severity: High
Advisory: GHSA-746v-hfh2-xphm
CVE: CVE-2022-38362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-17
Source: https://github.com/advisories/GHSA-746v-hfh2-xphm
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-docker` — affected >=0 <3.0.0

## Details
Apache Airflow Docker's Provider prior to 3.0.0 shipped with an example DAG that was vulnerable to (authenticated) remote code exploit of code on the Airflow worker host. Disable loading of example DAGs or upgrade apache-airflow-providers-docker to 3.0.0 or above.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38362
- https://lists.apache.org/thread/614p38nf4gbk8xhvnskj9b1sqo2dknkb
- http://www.openwall.com/lists/oss-security/2022/08/16/1
