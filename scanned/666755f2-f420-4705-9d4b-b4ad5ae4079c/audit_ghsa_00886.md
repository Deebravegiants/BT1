# [M] Cross-Site Scripting in dojo

## Summary
Severity: Medium
Advisory: GHSA-39cx-xcwj-3rc4
CVE: CVE-2008-6681
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-39cx-xcwj-3rc4
Type: github-advisory

## Affected
- npm: `dojo` — affected >=0 <1.1.0

## Details
Affected versions of `dojo` are susceptible to a cross-site scripting vulnerability in the `dijit.Editor` and `textarea` components, which execute their contents as Javascript, even when sanitized.


## Recommendation

Update to version 1.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-6681
- https://bugs.dojotoolkit.org/ticket/2140
- https://exchange.xforce.ibmcloud.com/vulnerabilities/49883
- https://www.npmjs.com/advisories/107
- http://trac.dojotoolkit.org/changeset/15346
- http://trac.dojotoolkit.org/ticket/2140
- http://www.dojotoolkit.org/book/dojo-1-1-release-notes
- http://www.securityfocus.com/bid/34661
