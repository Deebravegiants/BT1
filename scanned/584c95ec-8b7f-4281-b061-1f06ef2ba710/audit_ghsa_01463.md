# [H] Forgeable Public/Private Tokens in jws

## Summary
Severity: High
Advisory: GHSA-gjcw-v447-2w7q
CVE: CVE-2016-1000223
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-gjcw-v447-2w7q
Type: github-advisory

## Affected
- npm: `jws` — affected >=0 <3.0.0

## Details
Affected versions of the `jws` package allow users to select what algorithm the server will use to verify a provided JWT. A malicious actor can use this behaviour to arbitrarily modify the contents of a JWT while still passing verification. For the common use case of the JWT as a bearer token, the end result is a complete authentication bypass with minimal effort.




## Recommendation

Update to version 3.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000223
- https://github.com/brianloveswords/node-jws/commit/585d0e1e97b6747c10cf5b7689ccc5618a89b299#diff-4ac32a78649ca5bdd8e0ba38b7006a1e
- https://auth0.com/blog/2015/03/31/critical-vulnerabilities-in-json-web-token-libraries
- https://github.com/brianloveswords/node-jws
- https://snyk.io/vuln/npm:jws:20160726
- https://www.npmjs.com/advisories/88
