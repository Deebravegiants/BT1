# [H] Reflected XSS in GraphQL Playground

## Summary
Severity: High
Advisory: GHSA-4852-vrh7-28rf
CVE: CVE-2020-4038
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-06-09
Source: https://github.com/advisories/GHSA-4852-vrh7-28rf
Type: github-advisory

## Affected
- npm: `graphql-playground-html` — affected >=0 <1.6.22

## Details
### Impact

**directly impacted:**

- `graphql-playground-html@<1.6.22` - all unsanitized user input for `renderPlaygroundPage()`

**all of our consuming packages** of `graphql-playground-html` are impacted:

- `graphql-playground-middleware-express@<1.7.16` - unsanitized user input to `expressPlayground()`
- `graphql-playground-middleware-koa@<1.6.15` - unsanitized user input to `koaPlayground()`
- `graphql-playground-middleware-lambda@<1.7.17` - unsanitized user input to `lambdaPlayground()`
- `graphql-playground-middleware-hapi@<1.6.13` - unsanitized user input to `hapiPlayground()`

as well as ***any other packages*** that use these methods with unsanitized user input.

**not impacted:**

- `graphql-playground-electron` - uses `renderPlaygroundPage()` statically for a webpack build for electron bundle, no dynamic user input
- `graphql-playground-react` - usage of the component directly in a react application does not expose reflected XSS vulnerabilities. only the demo in `public/` contains the vulnerability, because it uses an old version of the html pacakge.

### Patches

upgrading to the above mentioned versions will solve the issue.

If you're using `graphql-playground-html` directly, then:

```
yarn add graphql-playground-html@^1.6.22
```

or

```
npm install --save graphql-playground-html@^1.6.22
```

Then, similar steps need to be taken for each middleware:

- [Upgrade Express Middleware](https://www.npmjs.com/package/graphql-playground-middleware-express#security-upgrade-steps)
- [Upgrade Koa Middleware](https://www.npmjs.com/package/graphql-playground-middleware-koa#security-upgrade-steps)
- [Upgrade Lambda Middleware](https://www.npmjs.com/package/graphql-playground-middleware-lambda#security-upgrade-steps)
- [Upgrade Hapi Middleware](https://www.npmjs.com/package/graphql-playground-middleware-hapi#security-upgrade-steps)

### Workarounds

Ensure you properly sanitize *all* user input for options you use for whatever function to initialize GraphQLPlayground:

for example, with `graphql-playground-html` and express:

```js
const { sanitizeUrl } = require('@braintree/sanitize-url');

const qs = require('querystringify');

const { renderPlaygroundPage } = require('graphql-playground-html');

module.exports = (req, res, next) => {
	const { endpoint } = qs.parse(req.url)
	res.html(renderPlaygroundPage({endpoint: sanitizeUrl(endpoint) })).status(200)
	next()
}
```

or, with `graphql-playground-express`:

```js
const { expressPlayground } = require('graphql-playground-middleware-express');
const { sanitizeUrl } = require('@braintree/sanitize-url');

const qs = require('querystringify');

const { renderPlaygroundPage } = require('graphql-playground-html');

module.exports = (req, res, next) => {
	const { endpoint } = qs.parse(req.url)
	res.html(expressPlayground({endpoint: sanitizeUrl(endpoint) })).status(200)
	next()
}
```

### References

- [OWASP: How to Test for CSS Reflection Attacks](https://github.com/OWASP/wstg/blob/master/document/4-Web_Application_Security_Testing/07-Input_Validation_Testing/01-Testing_for_Reflected_Cross_Site_Scripting.md)
- [Original Report from Cure53](https://user-images.githubusercontent.com/1368727/84191028-dfb7b980-aa65-11ea-8e18-4b8706f538e2.jpg) (jpg)


### Credits

Masato Kinugawa of Cure53

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [graphql-playground](https://github.com/prisma-labs/graphql-playground/issues/new/choose)
* Email us at [rikki.schulte@gmail.com](mailto:rikki.schulte@gmail.com)

## References
- https://github.com/graphql/graphql-playground/security/advisories/GHSA-4852-vrh7-28rf
- https://github.com/prisma-labs/graphql-playground/security/advisories/GHSA-4852-vrh7-28rf
- https://nvd.nist.gov/vuln/detail/CVE-2020-4038
- https://github.com/prisma-labs/graphql-playground/commit/bf1883db538c97b076801a60677733816cb3cfb7
- https://github.com/prisma-labs/graphql-playground#security-details
