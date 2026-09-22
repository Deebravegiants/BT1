# [H] Handlebars.js has Denial of Service via Malformed Decorator Syntax in Template Compilation

## Summary
Severity: High
Advisory: GHSA-9cx6-37pm-9jff
CVE: CVE-2026-33939
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-9cx6-37pm-9jff
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.7.9

## Details
## Summary

When a Handlebars template contains decorator syntax referencing an unregistered decorator (e.g. `{{*n}}`), the compiled template calls `lookupProperty(decorators, "n")`, which returns `undefined`. The runtime then immediately invokes the result as a function, causing an unhandled `TypeError: ... is not a function` that crashes the Node.js process. Any application that compiles user-supplied templates without wrapping the call in a `try/catch` is vulnerable to a single-request Denial of Service.

## Description

In `lib/handlebars/compiler/javascript-compiler.js`, the code generated for a decorator invocation looks like:

```javascript
fn = lookupProperty(decorators, "n")(fn, props, container, options) || fn;
```

When `"n"` is not a registered decorator, `lookupProperty(decorators, "n")` returns `undefined`. The expression immediately attempts to call `undefined` as a function, producing:

```
TypeError: lookupProperty(...) is not a function
```

Because the error is thrown inside the compiled template function and is not caught by the runtime, it propagates up as an unhandled exception and — when not caught by the application — crashes the Node.js process.

This inconsistency is notable: references to unregistered **helpers** produce a clean `"Missing helper: ..."` error, while references to unregistered **decorators** cause a hard crash.

**Attack scenario:** An attacker submits `{{*n}}` as template content to any endpoint that calls `Handlebars.compile(userInput)()`. Each request crashes the server process; with process managers that auto-restart (PM2, systemd), repeated submissions create a persistent DoS.

## Proof of Concept

```javascript
const Handlebars = require('handlebars'); // Handlebars 4.7.8, Node.js v22.x

// Any of these payloads crash the process
Handlebars.compile('{{*n}}')({});
Handlebars.compile('{{*decorator}}')({});
Handlebars.compile('{{*constructor}}')({});
```

Expected crash output:
```
TypeError: lookupProperty(...) is not a function
    at Function.eval [as decorator] (eval at compile (...javascript-compiler.js:134:36))
```

## Workarounds

- **Wrap compilation and rendering in `try/catch`:**
  ```javascript
  try {
    const result = Handlebars.compile(userInput)(context);
    res.send(result);
  } catch (err) {
    res.status(400).send('Invalid template');
  }
  ```
- **Validate template input** before passing it to `compile()`. Reject templates containing  decorator syntax (`{{*...}}`) if decorators are not used in your application.
- **Use the pre-compilation workflow:** compile templates at build time and serve only pre-compiled  templates; do not call `compile()` at request time.

## References
- https://github.com/handlebars-lang/handlebars.js/security/advisories/GHSA-9cx6-37pm-9jff
- https://nvd.nist.gov/vuln/detail/CVE-2026-33939
- https://github.com/handlebars-lang/handlebars.js/commit/68d8df5a88e0a26fe9e6084c5c6aaebe67b07da2
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.9
