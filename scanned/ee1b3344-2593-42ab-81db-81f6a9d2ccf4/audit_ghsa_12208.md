# [M] VBScript Content Injection in marked

## Summary
Severity: Medium
Advisory: GHSA-cfjh-p3g4-3q2f
CVE: CVE-2015-1370
CWE: CWE-79
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-cfjh-p3g4-3q2f
Type: github-advisory

## Affected
- npm: `marked` — affected >=0 <0.3.3

## Details
Versions 0.3.2 and earlier of `marked` are affected by a cross-site scripting vulnerability even when `sanitize:true` is set. 

## Proof of Concept ( IE10 Compatibility Mode Only )

`[xss link](vbscript:alert(1&#41;)`

will get a link

`<a href="vbscript:alert(1)">xss link</a>`


## Recommendation

Update to version 0.3.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1370
- https://github.com/chjj/marked/issues/492
- https://github.com/markedjs/marked/issues/492
- https://github.com/evilpacket/marked/commit/3c191144939107c45a7fa11ab6cb88be6694a1ba
- https://github.com/markedjs/marked/commit/fc372d1c6293267722e33f2719d57cebd67b3da1
- https://github.com/markedjs/marked
- https://www.npmjs.com/advisories/24
- https://www.npmjs.com/advisories/24/versions
- http://www.openwall.com/lists/oss-security/2015/01/23/2
