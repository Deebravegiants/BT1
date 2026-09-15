# [H] Prototype Pollution in fullpage.js

## Summary
Severity: High
Advisory: GHSA-vpgw-ffh3-648h
CVE: CVE-2022-1295
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-04-12
Source: https://github.com/advisories/GHSA-vpgw-ffh3-648h
Type: github-advisory

## Affected
- npm: `fullpage.js` — affected >=0 <4.0.2

## Details
fullPage utils are available to developers using window.fp_utils. They can use these utils for their own use-case (other than fullPage) as well. However, one of the utils deepExtend is vulnerable to Prototype Pollution vulnerability.

Javascript is "prototype" language which means when a new "object" is created, it carries the predefined properties and methods of an "object" with itself like toString, constructor etc. By using prototype-pollution vulnerability, an attacker can overwrite/create the property of that "object" type. If the victim developer has used that property anywhere in the code, then it will have severe effect on the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1295
- https://github.com/alvarotrigo/fullpage.js/commit/bf62492a22e5d296e63c3ed918a42fc5645a0d48
- https://github.com/alvarotrigo/fullpage.js
- https://huntr.dev/bounties/3b9d450c-24ac-4037-b04d-4d4dafbf593a
