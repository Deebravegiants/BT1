# [M] Apache Bookkeeper vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-gxq5-79m2-gvvq
CVE: CVE-2022-32531
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-gxq5-79m2-gvvq
Type: github-advisory

## Affected
- Maven: `org.apache.bookkeeper:bookkeeper-common` — affected >=0 <4.14.6
- Maven: `org.apache.bookkeeper:bookkeeper-common` — affected >=4.15.0 <4.15.1

## Details
The Apache Bookkeeper Java Client (before 4.14.6 and also 4.15.0) does not close the connection to the bookkeeper server when TLS hostname verification fails. This leaves the bookkeeper client vulnerable to a man in the middle attack. The problem affects BookKeeper client prior to versions 4.14.6 and 4.15.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32531
- https://github.com/apache/bookkeeper
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-bookkeeper-client/PYSEC-2022-43060.yaml
- https://lists.apache.org/thread/xyk2lfc7lzof8mksmwyympbqxts1b5s9
