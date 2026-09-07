# [H] Cross-Site Scripting in mustache

## Summary
Severity: High
Advisory: GHSA-w3w8-37jv-2c58
CVE: CVE-2015-8862
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-w3w8-37jv-2c58
Type: github-advisory

## Affected
- npm: `mustache` — affected >=0 <2.2.1

## Details
Versions of `mustache` prior to 2.2.1 are affected by a cross-site scripting vulnerability when attributes in mustache templates are not quoted.



### Example
Template:
```<a href={{foo}}/>```

Input:
```{ 'foo' : 'test.com onload=alert(1)'}```

Rendered result:
```<a href=test.com onload=alert(1)/>```


## Recommendation

Update to version 2.2.1 or later.
Alternatively, ensure that all attributes in hmustache templates are encapsulated with quotes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8862
- https://github.com/janl/mustache.js/commit/378bcca8a5cfe4058f294a3dbb78e8755e8e0da5
- https://github.com/advisories/GHSA-w3w8-37jv-2c58
- https://github.com/janl/mustache.js
- https://www.npmjs.com/advisories/62
- https://www.tenable.com/security/tns-2016-18
- http://www.openwall.com/lists/oss-security/2016/04/20/11
- http://www.securityfocus.com/bid/96436
