# [M] Cryptographically Weak PRNG in randomatic

## Summary
Severity: Medium
Advisory: GHSA-6g33-f262-xjp4
CVE: CVE-2017-16028
CWE: CWE-330, CWE-338
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-6g33-f262-xjp4
Type: github-advisory

## Affected
- npm: `randomatic` — affected >=0 <3.0.0

## Details
Affected versions of `randomatic` generate random values using a cryptographically weak psuedo-random number generator. This may result in predictable values instead of random values as intended.




## Recommendation

Update to version 3.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16028
- https://github.com/jonschlinkert/randomatic/commit/4a526959b3a246ae8e4a82f9c182180907227fe1#diff-b9cfc7f2cdf78a7f4b91a753d10865a2
- https://github.com/advisories/GHSA-6g33-f262-xjp4
- https://github.com/tableflip/react-native-meteor-oauth/blob/a7eb738b74c469f5db20296b44b7cae4e2337435/src/meteor-oauth.js#L66
- https://www.npmjs.com/advisories/157
