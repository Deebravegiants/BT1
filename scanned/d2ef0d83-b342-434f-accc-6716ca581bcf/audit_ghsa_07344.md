# [M] Quasar: Prototype pollution in the extend() utility

## Summary
Severity: Medium
Advisory: GHSA-3r53-75j5-3g7j
CVE: CVE-2026-73647
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-3r53-75j5-3g7j
Type: github-advisory

## Affected
- npm: `quasar` — affected >=0 <2.22.0

## Details
### Summary

`quasar@2.20.1`, the latest published version at the time of testing, appears to be vulnerable to prototype pollution through the public `extend()` utility exported from the package root.

When `extend(true, target, source)` is used for a deep merge, attacker-controlled object keys are recursively copied into the target object without blocking prototype-pollution primitives such as `__proto__`, `constructor`, or `prototype`.

This can allow attacker-controlled properties to be written to `Object.prototype`.

### Details

Affected source:

```text
src/utils/extend/extend.js
```

Distributed files include:

```text
dist/quasar.server.prod.js
dist/quasar.server.prod.cjs
dist/quasar.client.js
```

The package root publicly exports `extend`. During deep merge, source object keys are recursively assigned into the target object. If the source object contains an own `__proto__` property, the merge can descend into the prototype object and assign attacker-controlled properties onto `Object.prototype`.

### PoC

```bash
rm -rf /tmp/quasar-extend-pp-poc
mkdir /tmp/quasar-extend-pp-poc
cd /tmp/quasar-extend-pp-poc

npm init -y >/dev/null
npm install quasar@2.20.1 vue@3.5.31 >/dev/null

cat > hack.mjs <<'JS'
import { extend } from 'quasar';

delete Object.prototype.polluted;

extend(true, {}, {
  ['__proto__']: {
    polluted: 'yes'
  }
});

console.log(({}).polluted);

delete Object.prototype.polluted;
JS

node ./hack.mjs
```

Observed output:

```text
yes
```

Expected output:

```text
undefined
```

### Impact

This is a prototype pollution vulnerability.

If an application passes user-controlled or partially user-controlled objects into `extend(true, ...)`, an attacker may be able to pollute `Object.prototype` in the same JavaScript process.

Depending on how the polluted property is later consumed, this may lead to logic bypass, unsafe default option injection, denial of service, or other application-specific security impact.

### Suggested Fix

Reject or safely ignore dangerous keys before assignment, including:

```text
__proto__
prototype
constructor
```

The merge implementation should also avoid descending into prototype-related properties during recursive merge.

## References
- https://github.com/quasarframework/quasar/security/advisories/GHSA-3r53-75j5-3g7j
- https://github.com/quasarframework/quasar/commit/d0a95d95ab3c29d13e1b8ba8c5e5025fd6ce35e7
- https://github.com/quasarframework/quasar
- https://github.com/quasarframework/quasar/releases/tag/quasar-v2.22.0
