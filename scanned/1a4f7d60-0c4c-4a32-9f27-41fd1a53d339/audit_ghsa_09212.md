# [C] vm2: Mutable Proxies for Host Intrinsic Prototypes Allows Sandbox Escape

## Summary
Severity: Critical
Advisory: GHSA-vwrp-x96c-mhwq
CVE: CVE-2026-44005
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-vwrp-x96c-mhwq
Type: github-advisory

## Affected
- npm: `vm2` — affected >=3.9.6 <3.11.0

## Details
### Summary
vm2's bridge exposes mutable proxies for real host-realm intrinsic prototypes and then forwards sandbox writes into the underlying host objects with otherReflectSet() and otherReflectDefineProperty(), which lets attacker-controlled JavaScript running in a default VM or inherited NodeVM mutate shared host Object.prototype, Array.prototype, and Function.prototype from inside the sandbox.

### Details
BaseHandler.apply() unwraps sandbox-controlled receivers and arguments with otherFromThis() / otherFromThisArguments() and then directly invokes the real host function with ret = otherReflectApply(object, context, args), so any default-exposed host function that can surface a prototype getter becomes a prototype-walking primitive ([lib/bridge.js:665-676](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L665-L676)). BaseHandler.get() special-cases __proto__ and returns the host-side descriptor or proxy target prototype, which is enough for the attacker to reuse the host __lookupGetter__('__proto__') accessor repeatedly until the walk lands on host Object.prototype, Array.prototype, or Function.prototype ([lib/bridge.js:590-616](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L590-L616)). Once the attacker has a proxy to a host intrinsic prototype, BaseHandler.set() performs value = otherFromThis(value); return otherReflectSet(object, key, value) === true;, which writes attacker-controlled data directly into the shared host object instead of keeping the mutation sandbox-local; BaseHandler.defineProperty() repeats the same design at otherReflectDefineProperty(object, prop, otherDesc) for descriptor-based writes ([lib/bridge.js:641-649](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L641-L649), [lib/bridge.js:753-774](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L753-L774)). Existing validation does not stop the attack because the constructor filter only blocks one dangerous-property access pattern, setPrototypeOf() only blocks prototype replacement rather than ordinary property assignment, and containsDangerousConstructor() only protects one later re-unwrapping path instead of the initial host-prototype write sink ([lib/bridge.js:494-530](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L494-L530), [lib/bridge.js:595-610](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L595-L610), [lib/bridge.js:660-662](https://github.com/patriksimek/vm2/blob/408fc855f1cc1bbc2985b029465ee0e732ada433/lib/bridge.js#L660-L662)).

### PoC
Run the following code snippet and observe that the value of vm2EscapeMarker is polluted:
```
const { VM } = require('vm2');
const vm = new VM();
vm.run(`
  const g = ({}).__lookupGetter__;
  const a = Buffer.apply;
  const p = a.apply(g, [Buffer, ['__proto__']]);
  const hostObjectProto = p.call(p.call(p.call(p.call(Buffer.of()))));
  hostObjectProto.vm2EscapeMarker = 'polluted-object-prototype';
`);
console.log({}.vm2EscapeMarker)
```

### Impact
Sandbox escape and prototype pollution.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-vwrp-x96c-mhwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44005
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
