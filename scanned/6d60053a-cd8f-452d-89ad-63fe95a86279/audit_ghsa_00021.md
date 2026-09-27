# [C] XML External Entity (XXE) vulnerability in codelibs fess

## Summary
Severity: Critical
Advisory: GHSA-77hp-pfxw-4w63
CVE: CVE-2018-1000822
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-77hp-pfxw-4w63
Type: github-advisory

## Affected
- Maven: `org.codelibs.fess:fess` — affected >=0 <12.3.2

## Details
codelibs fess version before commit faa265b contains a XML External Entity (XXE) vulnerability in GSA XML file parser that can result in Disclosure of confidential data, denial of service, SSRF, port scanning. This attack appear to be exploitable via specially crafted GSA XML files. This vulnerability appears to have been fixed in after commit faa265b.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000822
- https://github.com/codelibs/fess/issues/1851
- https://0dd.zone/2018/10/27/fess-XXE
- https://github.com/advisories/GHSA-77hp-pfxw-4w63
- https://github.com/codelibs/fess
