# [M] Silverstripe XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-v358-rvxr-wffx
CVE: CVE-2012-4968
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v358-rvxr-wffx
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=2.3 <2.3.13
- Packagist: `silverstripe/framework` — affected >=2.4 <2.4.7

## Details
Multiple cross-site scripting (XSS) vulnerabilities in SilverStripe 2.3.x before 2.3.13 and 2.4.x before 2.4.7 allow remote attackers to inject arbitrary web script or HTML via 
1. a crafted string to the `AbsoluteLinks`
1. `BigSummary`
1. `ContextSummary`
1. `EscapeXML`
1. `FirstParagraph`
1. `FirstSentence`
1. `Initial`
1. `LimitCharacters`
1. `LimitSentences`
1. `LimitWordCount`
1. `LimitWordCountXML`
1. `Lower`
1. `LowerCase`
1. `NoHTML`
1. `Summary`
1. `Upper`
1. `UpperCase`, or 
1. `URL` method in a template, 

different vectors than CVE-2012-0976.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4968
- https://github.com/silverstripe/sapphire/commit/0085876
- https://github.com/silverstripe/silverstripe-framework/commit/0085876495f0f8dda5dc58cb24a8f2220e7baf1e
- https://github.com/silverstripe/silverstripe-framework/commit/15e9e059e5948ccf8f5a36dfcb435ad26ecec334
- https://github.com/silverstripe/silverstripe-framework
- http://doc.silverstripe.org/framework/en/trunk/changelogs/2.3.13
- http://doc.silverstripe.org/framework/en/trunk/changelogs/2.4.7
- http://www.openwall.com/lists/oss-security/2012/04/30/1
- http://www.openwall.com/lists/oss-security/2012/04/30/3
