# [H] CVE-2021-21277

## Summary
Severity: High
Advisory: CVE-2021-21277
Aliases: GHSA-j6px-jwvv-vpwq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-01
Source: https://osv.dev/vulnerability/CVE-2021-21277
Type: osv

## Details
angular-expressions is "angular's nicest part extracted as a standalone module for the browser and node". In angular-expressions before version 1.1.2 there is a vulnerability which allows Remote Code Execution if you call "expressions.compile(userControlledInput)" where "userControlledInput" is text that comes from user input. The security of the package could be bypassed by using a more complex payload, using a ".constructor.constructor" technique. In terms of impact: If running angular-expressions in the browser, an attacker could run any browser script when the application code calls expressions.compile(userControlledInput). If running angular-expressions on the server, an attacker could run any Javascript expression, thus gaining Remote Code Execution. This is fixed in version 1.1.2 of angular-expressions A temporary workaround might be either to disable user-controlled input that will be fed into angular-expressions in your application or allow only following characters in the userControlledInput.

## References
- https://www.npmjs.com/package/angular-expressions
- http://blog.angularjs.org/2016/09/angular-16-expression-sandbox-removal.html
- https://github.com/peerigon/angular-expressions/security/advisories/GHSA-j6px-jwvv-vpwq
- https://github.com/peerigon/angular-expressions/commit/07edb62902b1f6127b3dcc013da61c6316dd0bf1
