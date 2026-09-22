# [M] Apache Airflow AWS Auth Manager has Host Header Injection Leading to SAML Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-rv5f-ccpm-xjj4
CVE: CVE-2026-25604
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-rv5f-ccpm-xjj4
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-amazon` — affected >=0 <9.22.0

## Details
In AWS Auth manager, the origin of the SAML authentication has been used as provided by the client and not verified against the actual instance URL. 
This allowed to gain access to different instances with potentially different access controls by reusing SAML response from other instances.

You should upgrade to 9.22.0 version of provider if you use AWS Auth Manager.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25604
- https://github.com/apache/airflow/pull/61368
- https://github.com/apache/airflow/commit/1a86aec01d827ba8caf41b645db56663a9a61850
- https://github.com/apache/airflow
- https://lists.apache.org/thread/spwwrsmwxod7fpttcd7n7zs46j839l77
- http://www.openwall.com/lists/oss-security/2026/03/09/6
