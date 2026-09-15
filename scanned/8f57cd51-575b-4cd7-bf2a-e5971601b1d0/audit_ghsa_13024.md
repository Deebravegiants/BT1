# [M] Apache Airflow missing Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-5f35-pq34-c87q
CVE: CVE-2023-39441
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-5f35-pq34-c87q
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-smtp` — affected >=0 <1.3.0
- PyPI: `apache-airflow-providers-imap` — affected >=0 <3.3.0
- PyPI: `apache-airflow` — affected >=0 <2.7.0

## Details
Apache Airflow SMTP Provider before 1.3.0, Apache Airflow IMAP Provider before 3.3.0, and Apache Airflow before 2.7.0 are affected by the Validation of OpenSSL Certificate vulnerability.

The default SSL context with SSL library did not check a server's X.509 certificate.  Instead, the code accepted any certificate, which could result in the disclosure of mail server credentials or mail contents when the client connects to an attacker in a MITM position.

Users are strongly advised to upgrade to Apache Airflow version 2.7.0 or newer, Apache Airflow IMAP Provider version 3.3.0 or newer, and Apache Airflow SMTP Provider version 1.3.0 or newer to mitigate the risk associated with this vulnerability

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39441
- https://github.com/apache/airflow/pull/33070
- https://github.com/apache/airflow/pull/33075
- https://github.com/apache/airflow/pull/33108
- https://github.com/apache/airflow/commit/38fc9cd823feafd8ec61d5d5c7eddb9e9162f755
- https://github.com/apache/airflow/commit/3bd8f020e8b7bdeb7f618bdbdfb3557f117b29d3
- https://github.com/apache/airflow/commit/dbacacbd4d476da757de148a4e747924c34fd7fe
- https://github.com/apache/airflow
- https://lists.apache.org/thread/xzp4wgjg2b1o6ylk2595df8bstlbo1lb
- http://www.openwall.com/lists/oss-security/2023/08/23/2
