# [H] Apache Airflow denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-x2mh-8fmc-rqgh
CVE: CVE-2023-37379
CWE: CWE-200, CWE-400, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-x2mh-8fmc-rqgh
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.7.0b1

## Details
Apache Airflow, in versions prior to 2.7.0, contains a security vulnerability that can be exploited by an authenticated user possessing Connection edit privileges. This vulnerability allows the user to access connection information and exploit the test connection feature by sending many requests, leading to a denial of service (DoS) condition on the server. Furthermore, malicious actors can leverage this vulnerability to establish harmful connections with the server.

Users of Apache Airflow are strongly advised to upgrade to version 2.7.0 or newer to mitigate the risk associated with this vulnerability. Additionally, administrators are encouraged to review and adjust user permissions to restrict access to sensitive functionalities, reducing the attack surface.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37379
- https://github.com/apache/airflow/pull/32052
- https://github.com/apache/airflow/commit/e4c3ecf8ceaefa17525b495e4bcb5b2f41309603
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-152.yaml
- https://lists.apache.org/thread/g5c9vcn27lr14go48thrjpo6f4vw571r
- http://www.openwall.com/lists/oss-security/2023/08/23/4
