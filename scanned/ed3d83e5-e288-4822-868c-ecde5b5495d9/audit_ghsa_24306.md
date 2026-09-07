# [M] Joomla! vulnerable to CRLF injection

## Summary
Severity: Medium
Advisory: GHSA-h22q-g2c7-2jwj
CVE: CVE-2007-4190
CWE: CWE-93
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-h22q-g2c7-2jwj
Type: github-advisory

## Affected
- Packagist: `joomla/application` — affected >=0 <1.0.13

## Details
CRLF injection vulnerability in Joomla! before 1.0.13 (aka Sunglow) allows remote attackers to inject arbitrary HTTP headers and probably conduct HTTP response splitting attacks via CRLF sequences in the url parameter.  NOTE: this can be leveraged for cross-site scripting (XSS) attacks.  NOTE: some of these details are obtained from third party information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-4190
- https://github.com/joomla/joomla-cms
- https://web.archive.org/web/20071001212343/http://www.joomla.org/content/view/3677/1
