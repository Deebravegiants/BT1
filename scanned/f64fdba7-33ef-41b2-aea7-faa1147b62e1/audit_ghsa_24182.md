# [M] SilverStripe XXE Vulnerability in CSSContentParser

## Summary
Severity: Medium
Advisory: GHSA-3vjc-5x79-m9r8
CVE: CVE-2020-25817
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3vjc-5x79-m9r8
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.7.4

## Details
SilverStripe through 4.6.0-rc1 has an XXE Vulnerability in CSSContentParser. A developer utility meant for parsing HTML within unit tests can be vulnerable to XML External Entity (XXE) attacks. When this developer utility is misused for purposes involving external or user submitted data in custom project code, it can lead to vulnerabilities such as XSS on HTML output rendered through this custom code. This is now mitigated by disabling external entities during parsing. (The correct CVE ID year is 2020 [CVE-2020-25817, not CVE-2021-25817]).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25817
- https://forum.silverstripe.org/c/releases
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2021-25817
