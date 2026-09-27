# [M] XSS Filter Bypass via Encoded URL in validator

## Summary
Severity: Medium
Advisory: GHSA-79mx-88w7-8f7q
CVE: CVE-2014-9772
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-79mx-88w7-8f7q
Type: github-advisory

## Affected
- npm: `validator` — affected >=0 <2.0.0

## Details
Versions of `validator` prior to 2.0.0 contained an xss filter method that is affected by several filter bypasses. This may result in a cross-site scripting vulnerability.


## Proof of Concept
The xss() function removes the word "javascript" when contained inside an attribute.

However, it does not properly handle cases where characters have been hex-encoded. 

As a result, it is possible to build an input that bypasses the filter but which the browser will accept as valid JavaScript.

For example:
```<a href="jav&#x61;script:...">abc</a>```
will render as:
```<a href="javascript:...">abc</a>```


## Recommendation

The package author has decided to remove the xss filter functionality in the latest version of this module. If this feature is not currently being used, you are not affected by the vulnerability. If it is being used, updating to the latest version of the module will break your application.

In order for affected users to mitigate this vulnerability, it is necessary to use an [alternative package](https://www.npmjs.com/search?q=xss%20filter&page=1&ranking=optimal) that provides similar functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9772
- https://github.com/chriso/validator.js/issues/181
- https://github.com/advisories/GHSA-79mx-88w7-8f7q
- https://github.com/chriso/validator.js
- https://www.npmjs.com/advisories/43
- http://www.openwall.com/lists/oss-security/2016/04/20/11
- http://www.securityfocus.com/bid/97102
