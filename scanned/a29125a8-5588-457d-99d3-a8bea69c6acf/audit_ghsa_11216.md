# [H] Handlebars.js has JavaScript Injection via AST Type Confusion when passing an object as dynamic partial

## Summary
Severity: High
Advisory: GHSA-xhpv-hc6g-r9c6
CVE: CVE-2026-33940
CWE: CWE-843, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-xhpv-hc6g-r9c6
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.7.9

## Details
## Summary

A crafted object placed in the template context can bypass all conditional guards in `resolvePartial()` and cause `invokePartial()` to return `undefined`. The Handlebars runtime then treats the unresolved partial as a source that needs to be compiled, passing the crafted object to `env.compile()`. Because the object is a valid Handlebars AST containing injected code, the generated JavaScript executes arbitrary commands on the server. The attack requires the adversary to control a value that can be returned by a dynamic partial lookup.

## Description

The vulnerable code path spans two functions in `lib/handlebars/runtime.js`:

**`resolvePartial()`:** A crafted object with `call: true` satisfies the first branch condition (`partial.call`) and causes an early return of the original object itself, because none of the remaining conditionals (string check, `options.partials` lookup, etc.) match a plain object. The function returns the crafted object as-is.

**`invokePartial()`:** When `resolvePartial` returns a non-function object, `invokePartial` produces `undefined`. The runtime interprets `undefined` as "partial not yet compiled" and calls `env.compile(partial, ...)` where `partial` is the crafted AST object. The JavaScript code generator processes the AST and emits JavaScript containing the injected payload, which is then evaluated.

**Minimum prerequisites:**
1. The template uses a dynamic partial lookup: `{{> (lookup . "key")}}` or equivalent.
2. The adversary can set the value of the looked-up context property to a crafted object.

In server-side rendering scenarios where templates process user-supplied context data, this enables full Remote Code Execution.

## Proof of Concept

```javascript
const Handlebars = require('handlebars');

const vulnerableTemplate = `{{> (lookup . "payload")}}`;

const maliciousContext = {
  payload: {
    call: true, // bypasses the primary resolvePartial branch
    type: "Program",
    body: [
      {
        type: "MustacheStatement",
        depth: 0,
        path: {
          type: "PathExpression",
          parts: ["pop"],
          original: "this.pop",
          // Injected code breaks out of the generated function's argument list
          depth: "0])),function () {console.error('VULNERABLE: object -> dynamic partial -> RCE');}()));//",
        },
      },
    ],
  },
};

Handlebars.compile(vulnerableTemplate)(maliciousContext);
// Prints: VULNERABLE: object -> dynamic partial -> RCE
```

## Workarounds

- **Use the runtime-only build** (`require('handlebars/runtime')`). Without `compile()`,  the fallback compilation path in `invokePartial` is unreachable.
- **Sanitize context data** before rendering: ensure no value in the context is a non-primitive  object that could be passed to a dynamic partial.
- **Avoid dynamic partial lookups** (`{{> (lookup ...)}}`) when context data is user-controlled.

## References
- https://github.com/handlebars-lang/handlebars.js/security/advisories/GHSA-xhpv-hc6g-r9c6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33940
- https://github.com/handlebars-lang/handlebars.js/commit/68d8df5a88e0a26fe9e6084c5c6aaebe67b07da2
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.9
