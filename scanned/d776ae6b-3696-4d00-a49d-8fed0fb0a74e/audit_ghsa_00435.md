# [M] OWASP AntiSamy vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-683w-6h9j-57wq
CVE: CVE-2016-10006
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-683w-6h9j-57wq
Type: github-advisory

## Affected
- Maven: `org.owasp.antisamy:antisamy` — affected >=0 <1.5.5

## Details
In OWASP AntiSamy before 1.5.5, by submitting a specially crafted input (a tag that supports style with active content), you could bypass the library protections and supply executable code. The impact is XSS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10006
- https://github.com/nahsra/antisamy/issues/2
- https://github.com/nahsra/antisamy
- https://web.archive.org/web/20170214025813/http://www.securityfocus.com/bid/95101
- https://web.archive.org/web/20201207192053/http://www.securitytracker.com/id/1037532
