# [M] Cross-Site Scripting in morris.js

## Summary
Severity: Medium
Advisory: GHSA-fwx5-5fqj-jv98
CVE: CVE-2017-16022
CWE: CWE-79
Ecosystem: npm
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-fwx5-5fqj-jv98
Type: github-advisory

## Affected
- npm: `morris.js` — affected 0.5.0

## Details
Affected versions of `morris.js` are vulnerable to cross-site scripting attacks in labels that appear when hovering over a particular point on a generated graph. The text content of these labels is not escaped, so if control over the labels is obtained, script can be injected. The script will run on the client side whenever that specific graph is loaded.


## Recommendation

A patch for this vulnerability was created in 2014, but has still not been published to npm. In order to mitigate this issue effectively, install the library from github via:
```
npm i morrisjs/morris.js -s
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16022
- https://github.com/morrisjs/morris.js/pull/464
- https://github.com/advisories/GHSA-fwx5-5fqj-jv98
- https://www.npmjs.com/advisories/307
