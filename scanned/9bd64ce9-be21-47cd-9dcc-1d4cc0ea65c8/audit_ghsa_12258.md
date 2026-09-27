# [C] Arbitrary JavaScript Execution in bassmaster

## Summary
Severity: Critical
Advisory: GHSA-5j3g-jfq3-7jwx
CVE: CVE-2014-7205
CWE: CWE-94
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-5j3g-jfq3-7jwx
Type: github-advisory

## Affected
- npm: `bassmaster` — affected >=0 <1.5.2

## Details
A vulnerability exists in bassmaster <= 1.5.1 that allows for an attacker to provide arbitrary JavaScript that is then executed server side via eval.


## Recommendation

Update to bassmaster version 1.5.2 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7205
- https://github.com/hapijs/bassmaster/commit/b751602d8cb7194ee62a61e085069679525138c4
- https://exchange.xforce.ibmcloud.com/vulnerabilities/96730
- https://github.com/advisories/GHSA-5j3g-jfq3-7jwx
- https://github.com/hapijs/bassmaster
- https://www.exploit-db.com/exploits/40689
- https://www.npmjs.com/advisories/1
- http://www.openwall.com/lists/oss-security/2014/09/30/10
- http://www.securityfocus.com/bid/70180
