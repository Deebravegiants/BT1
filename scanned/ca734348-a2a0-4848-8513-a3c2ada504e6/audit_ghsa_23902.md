# [M] SOAPpy vulnerable to XML External Entity attacks

## Summary
Severity: Medium
Advisory: GHSA-52wr-3vww-rmpq
CVE: CVE-2014-3242
CWE: CWE-611
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-52wr-3vww-rmpq
Type: github-advisory

## Affected
- PyPI: `SOAPpy` — affected >=0

## Details
SOAPpy 0.12.5 allows remote attackers to read arbitrary files via a SOAP request containing an external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3242
- https://github.com/kiorky/soappy
- https://web.archive.org/web/20150501220613/http://www.pnigos.com/?p=260
- https://web.archive.org/web/20200229062311/http://www.securityfocus.com/bid/67216
- http://seclists.org/fulldisclosure/2014/May/20
- http://www.openwall.com/lists/oss-security/2014/05/06/1
- http://www.openwall.com/lists/oss-security/2014/05/06/9
