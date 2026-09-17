# [C] RSA-PSS signature validation vulnerability by prepending zeros in jsrsasign

## Summary
Severity: Critical
Advisory: GHSA-q3gh-5r98-j4h3
CVE: CVE-2020-14968
CWE: CWE-119
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-26
Source: https://github.com/advisories/GHSA-q3gh-5r98-j4h3
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=3.0.0 <8.0.17

## Details
### Impact
Jsrsasign can verify RSA-PSS signature which value can expressed as BigInteger. When there is a valid RSA-PSS signature value, this vulnerability is also accept value with prepending zeros as a valid signature.

- If you are not use RSA-PSS signature validation, this vulnerability is not affected. 
- Risk to accept a forged or crafted message to be signed is low.
- Risk to raise memory corruption is low since jsrsasign uses BigInteger class.

### Patches
Users using RSA-PSS signature validation should upgrade to 8.0.17.

### Workarounds
Reject RSA-PSS signatures with unnecessary prepending zeros.

### References
https://github.com/kjur/jsrsasign/security/advisories/GHSA-q3gh-5r98-j4h3
[https://github.com/kjur/jsrsasign/issues/438](https://github.com/kjur/jsrsasign/issues/438)
https://nvd.nist.gov/vuln/detail/CVE-2020-14968
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14968
https://vuldb.com/?id.157125
https://kjur.github.io/jsrsasign/api/symbols/RSAKey.html#.verifyWithMessageHashPSS

## References
- https://github.com/kjur/jsrsasign/security/advisories/GHSA-q3gh-5r98-j4h3
- https://nvd.nist.gov/vuln/detail/CVE-2020-14968
- https://github.com/kjur/jsrsasign/issues/438
- https://github.com/kjur/jsrsasign/commit/3bcc088c727658d7235854cd2a409a904cc2ce99
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-14968
- https://github.com/kjur/jsrsasign
- https://github.com/kjur/jsrsasign/releases/tag/8.0.17
- https://github.com/kjur/jsrsasign/releases/tag/8.0.18
- https://kjur.github.io/jsrsasign
- https://kjur.github.io/jsrsasign/api/symbols/RSAKey.html#.verifyWithMessageHashPSS
- https://security.netapp.com/advisory/ntap-20200724-0001
- https://vuldb.com/?id.157125
- https://www.npmjs.com/advisories/1541
- https://www.npmjs.com/package/jsrsasign
