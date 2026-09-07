# [M] Apache Druid before 0.23.0 vulnerable to reflected XSS via unescaped URL parameters

## Summary
Severity: Medium
Advisory: GHSA-8rmv-98m4-g5c6
CVE: CVE-2021-44791
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-08
Source: https://github.com/advisories/GHSA-8rmv-98m4-g5c6
Type: github-advisory

## Affected
- Maven: `org.apache.druid:druid` — affected >=0 <0.23.0

## Details
In Apache Druid 0.22.1 and earlier, certain specially-crafted links result in unescaped URL parameters being sent back in HTML responses. This makes it possible to execute reflected XSS attacks. This issue is patched in version 0.23.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-44791
- https://github.com/apache/druid
- https://lists.apache.org/thread/lh2kcl4j45q7xj4w6rqf6kwf0mvyp2o6
