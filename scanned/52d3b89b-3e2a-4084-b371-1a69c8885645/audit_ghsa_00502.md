# [M] Cross-Site Scripting in handlebars

## Summary
Severity: Medium
Advisory: GHSA-9prh-257w-9277
CVE: CVE-2015-8861
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-23
Source: https://github.com/advisories/GHSA-9prh-257w-9277
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=0 <4.0.0

## Details
Versions of `handlebars` prior to 4.0.0 are affected by a cross-site scripting vulnerability when attributes in handlebar templates are not quoted.


## Proof of Concept
Template:
```<a href={{foo}}/>```

Input:
```{ 'foo' : 'test.com onload=alert(1)'}```

Rendered result:
```<a href=test.com onload=alert(1)/>```


## Recommendation

Update to version 4.0.0 or later.
Alternatively, ensure that all attributes in handlebars templates are encapsulated with quotes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8861
- https://github.com/wycats/handlebars.js/pull/1083
- https://blog.srcclr.com/handlebars_vulnerability_research_findings
- https://github.com/advisories/GHSA-9prh-257w-9277
- https://github.com/wycats/handlebars.js
- https://www.npmjs.com/advisories/61
- https://www.sourceclear.com/blog/handlebars_vulnerability_research_findings
- https://www.tenable.com/security/tns-2016-18
- http://www.openwall.com/lists/oss-security/2016/04/20/11
- http://www.securityfocus.com/bid/96434
