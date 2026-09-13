# [H] Apache Struts has a Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-rg58-xhh7-mqjw
CVE: CVE-2025-66675
CWE: CWE-459
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-rg58-xhh7-mqjw
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=2.0.0 <6.8.0
- Maven: `org.apache.struts:struts2-core` — affected >=7.0.0 <7.1.1

## Details
Denial of Service vulnerability in Apache Struts, file leak in multipart request processing causes disk exhaustion.

This issue affects Apache Struts: from 2.0.0 through 6.7.4, from 7.0.0 through 7.0.3.

Users are recommended to upgrade to version 6.8.0 or 7.1.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-66675
- https://github.com/apache/struts/commit/831568929cfba700f790f6ebe6e335f9f33fb468
- https://cve.org/CVERecord?id=CVE-2025-64775
- https://cwiki.apache.org/confluence/display/WW/S2-068
- https://github.com/apache/struts
