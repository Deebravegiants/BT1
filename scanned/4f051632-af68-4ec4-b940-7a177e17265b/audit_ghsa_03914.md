# [H] Downloads Resources over HTTP in operadriver

## Summary
Severity: High
Advisory: GHSA-2wrq-wmqf-8vcc
CVE: CVE-2016-10565
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-2wrq-wmqf-8vcc
Type: github-advisory

## Affected
- npm: `operadriver` — affected >=0 <0.2.3

## Details
operadriver is a Opera Driver for Selenium.

operadriver versions below 0.2.3 download binary resources over HTTP, which leaves it vulnerable to MITM attacks.  It may be possible to cause remote code execution (RCE) by swapping out the requested binary with an attacker controlled binary if the attacker is on the network or positioned in between the user and the remote server.


## Recommendation

Update to version 0.2.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10565
- https://github.com/advisories/GHSA-2wrq-wmqf-8vcc
- https://www.npmjs.com/advisories/196
