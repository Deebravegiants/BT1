# [H] JWS and JWT signature validation vulnerability with special characters

## Summary
Severity: High
Advisory: GHSA-3fvg-4v2m-98jf
CVE: CVE-2022-25898
CWE: CWE-347
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-06-25
Source: https://github.com/advisories/GHSA-3fvg-4v2m-98jf
Type: github-advisory

## Affected
- npm: `jsrsasign` — affected >=4.8.0 <10.5.25

## Details
### Impact

Jsrsasign supports JWS(JSON Web Signatures) and JWT(JSON Web Token) validation. However JWS or JWT signature with non Base64URL encoding special characters or number escaped characters may be validated as valid by mistake.

For example, even if a string of non Base64URL encoding characters such as `!@$%` or `\11` is inserted into a valid JWS or JWT signature value string, it will still be a valid JWS or JWT signature by mistake.

When jsrsasign's JWS or JWT validation is used in OpenID connect or OAuth2, this vulnerability will affect to authentication or authorization.

By our internal assessment, CVSS 3.1 score will be 8.6.
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N

### Patches
Users validate JWS or JWT signatures should upgrade to 10.5.25.

### Workarounds
Validate JWS or JWT signature if it has Base64URL and dot safe string before
executing JWS.verify() or JWS.verifyJWT() method.

### ACKNOWLEDGEMENT

Thanks to Adi Malyanker and Or David for this vulnerability report. Also thanks for [Snyk security team](https://snyk.io/) for this coordination.

### References
https://github.com/kjur/jsrsasign/releases/tag/10.5.25
https://github.com/kjur/jsrsasign/security/advisories/GHSA-3fvg-4v2m-98jf kjur's advisories
https://github.com/advisories/GHSA-3fvg-4v2m-98jf github advisories
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-25898
https://kjur.github.io/jsrsasign/api/symbols/KJUR.jws.JWS.html#.verifyJWT
https://kjur.github.io/jsrsasign/api/symbols/KJUR.jws.JWS.html#.verify
https://kjur.github.io/jsrsasign/api/symbols/global__.html#.isBase64URLDot
https://github.com/kjur/jsrsasign/wiki/Tutorial-for-JWS-verification
https://github.com/kjur/jsrsasign/wiki/Tutorial-for-JWT-verification
https://security.snyk.io/vuln/SNYK-JS-JSRSASIGN-2869122

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25898
- https://github.com/kjur/jsrsasign/commit/4536a6e9e8bcf1a644ab7c07ed96e453347dae41
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-25898
- https://github.com/kjur/jsrsasign
- https://github.com/kjur/jsrsasign/releases/tag/10.5.25
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-2935898
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBKJUR-2935897
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2935896
- https://snyk.io/vuln/SNYK-JS-JSRSASIGN-2869122
