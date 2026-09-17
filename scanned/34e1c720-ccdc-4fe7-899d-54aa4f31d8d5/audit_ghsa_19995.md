# [H] Apache CXF vulnerable to Exposure of Sensitive Information

## Summary
Severity: High
Advisory: GHSA-3w37-5p3p-jv92
CVE: CVE-2022-46363
CWE: CWE-20, CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-3w37-5p3p-jv92
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.4.10
- Maven: `org.apache.cxf:cxf-core` — affected >=3.5.0 <3.5.5

## Details
A vulnerability in Apache CXF before versions 3.5.5 and 3.4.10 allows an attacker to perform a remote directory listing or code exfiltration. The vulnerability only applies when the CXFServlet is configured with both the static-resources-list and redirect-query-check attributes. These attributes are not supposed to be used together, and so the vulnerability can only arise if the CXF service is misconfigured.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46363
- https://github.com/apache/cxf
- https://lists.apache.org/thread/pdzo1qgyplf4y523tnnzrcm7hoco3l8c
