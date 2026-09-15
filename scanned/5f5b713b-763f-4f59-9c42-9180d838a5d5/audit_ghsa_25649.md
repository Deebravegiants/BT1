# [H] OutOfMemory Exception by specifically crafted processing instruction in NekoHtml Parser

## Summary
Severity: High
Advisory: GHSA-6jmm-mp6w-4rrg
CVE: CVE-2022-29546
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-6jmm-mp6w-4rrg
Type: github-advisory

## Affected
- Maven: `net.sourceforge.htmlunit:neko-htmlunit` — affected >=0 <2.61.0

## Details
### Impact
NekoHtml Parser suffers from a denial of service vulnerability on versions 2.60.0 and below. A specifically crafted input regarding the parsing of processing instructions leads to heap memory consumption. Please update to version 2.61.0.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/HtmlUnit/htmlunit-neko](https://github.com/HtmlUnit/htmlunit-neko)
* Email us at [rbri at rbri.de]

## References
- https://github.com/HtmlUnit/htmlunit-neko/security/advisories/GHSA-6jmm-mp6w-4rrg
- https://nvd.nist.gov/vuln/detail/CVE-2022-29546
- https://github.com/HtmlUnit/htmlunit-neko/commit/9d2aecd69223469e40c12ca3edddda09009110cc
- https://github.com/HtmlUnit/htmlunit-neko
