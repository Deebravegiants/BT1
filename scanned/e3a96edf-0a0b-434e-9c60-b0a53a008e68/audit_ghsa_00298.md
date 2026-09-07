# [H] npm Token Leak in npm

## Summary
Severity: High
Advisory: GHSA-m5h6-hr3q-22h5
CVE: CVE-2016-3956
CWE: CWE-200
Ecosystem: npm
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-m5h6-hr3q-22h5
Type: github-advisory

## Affected
- npm: `npm` — affected >=0 <2.15.1
- npm: `npm` — affected >=3.0.0 <3.8.3

## Details
Affected versions of the `npm` package include the bearer token of the logged in user in every request made by the CLI, even if the request is not directed towards the user's active registry. 

An attacker could create an HTTP server to collect tokens, and by various means including but not limited to install scripts, cause the npm CLI to make a request to that server, which would compromise the user's token.

This compromised token could be used to do anything that the user could do, including publishing new packages.




## Recommendation

1. Update npm with `npm install npm@latest -g`
2. [Revoke your Tokens](https://www.npmjs.com/settings/tokens)
3. Enable [Two-Factor Authentication](https://docs.npmjs.com/getting-started/using-two-factor-authentication)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3956
- https://github.com/npm/npm/issues/8380
- https://github.com/npm/npm/commit/f67ecad59e99a03e5aad8e93cd1a086ae087cb29
- https://github.com/npm/npm/commit/fea8cc92cee02c720b58f95f14d315507ccad401
- https://github.com/advisories/GHSA-m5h6-hr3q-22h5
- https://nodejs.org/en/blog/vulnerability/npm-tokens-leak-march-2016
- https://www.npmjs.com/advisories/98
- http://blog.npmjs.org/post/142036323955/fixing-a-bearer-token-vulnerability
- http://www-01.ibm.com/support/docview.wss?uid=swg21980827
