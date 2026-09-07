# [M] Apache Superset Stored XSS on Dashboard markdown

## Summary
Severity: Medium
Advisory: GHSA-w358-rj93-r5qv
CVE: CVE-2021-27907
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-w358-rj93-r5qv
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <0.38.1

## Details
Apache Superset up to and including 0.38.0 allowed the creation of a Markdown component on a Dashboard page for describing chart's related information. Abusing this functionality, a malicious user could inject javascript code executing unwanted action in the context of the user's browser. The javascript code will be automatically executed (Stored XSS) when a legitimate user surfs on the dashboard page. The vulnerability is exploitable creating a “div” section and embedding in it a “svg” element with javascript code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27907
- https://github.com/advisories/GHSA-w358-rj93-r5qv
- https://github.com/apache/superset
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-superset/PYSEC-2021-127.yaml
- https://lists.apache.org/thread.html/r09293fb09f1d617f0d2180c42210e739e2211f8da9bc5c1873bea67a%40%3Cdev.superset.apache.org%3E
- https://lists.apache.org/thread.html/r09293fb09f1d617f0d2180c42210e739e2211f8da9bc5c1873bea67a@%3Cdev.superset.apache.org%3E
