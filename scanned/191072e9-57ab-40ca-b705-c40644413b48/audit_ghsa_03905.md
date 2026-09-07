# [H] Sails before 0.12.7 vulnerable to Broken CORS

## Summary
Severity: High
Advisory: GHSA-qmv4-jgp7-mf68
CVE: CVE-2016-10549
CWE: CWE-284
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-qmv4-jgp7-mf68
Type: github-advisory

## Affected
- npm: `sails` — affected >=0 <0.12.7

## Details
Affected versions of `sails` have an issue with the CORS configuration where the value of the origin header is reflected as the value for the `Access-Control-Allow-Origin` header. This may allow an attacker to make AJAX requests to vulnerable hosts through cross-site scripting or a malicious HTML Document, effectively bypassing the Same Origin Policy. 

## Mitigating Factors

This is only an issue when `allRoutes` is set to `true` and `origin` is set to `*` or left commented out in the sails CORS config file. 

The problem can be compounded when the cors `credentials` setting is not provided, because at that point authenticated cross domain requests are possible.


## Recommendation

Update to version 0.12.7 or later.

As this vulnerability is primarily a user error, the patch for the vulnerability will simply cause the application to write an error message to the console when a vulnerable configuration is used in a production environment.

Writing a proper CORS configuration is still the responsibility of the user, so it is necessary to check for the error message after installing the patch. Be sure you are not using `allRoutes: true` with `origin:'*'`, and that you uncomment `origin` and set it to a reasonable value. Ensure that if `origin` is set to `*` that you truly mean for all other websites to be able to make cross-domain requests to your API.

Likewise, ensure `credentials` is uncommented out and set to the appropriate value. Make sure to explicitly set which origins may request resources via CORS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10549
- https://github.com/balderdashy/sails/commit/0057123a0321be6758845abbeb4290bf418ce542
- https://github.com/balderdashy/sails
- https://github.com/balderdashy/sails/releases/tag/v0.12.7
- https://www.npmjs.com/advisories/148
- http://sailsjs.org/documentation/concepts/security/cors
- http://sailsjs.org/documentation/reference/configuration/sails-config-cors
