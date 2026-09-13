# [H] Apache Jena Expression Language Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-j927-w6g7-7c7w
CVE: CVE-2023-32200
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-j927-w6g7-7c7w
Type: github-advisory

## Affected
- Maven: `org.apache.jena:jena` — affected >=3.7.0 <4.9.0

## Details
There is insufficient restrictions of called script functions in Apache Jena versions 4.8.0 and earlier. It allows a remote user to execute javascript via a SPARQL query. This issue affects Apache Jena from 3.7.0 through 4.8.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-32200
- https://github.com/apache/jena
- https://jena.apache.org/about_jena/security-advisories.html#cve-2023-32200---exposure-of-execution-in-script-engine-expressions
- https://lists.apache.org/thread/7hg0t2kws3fyr75dl7lll8389xzzc46z
- https://www.cve.org/CVERecord?id=CVE-2023-22665
