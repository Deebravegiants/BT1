# [M] uuid: Missing buffer bounds check in v3/v5/v6 when buf is provided

## Summary
Severity: Medium
Advisory: GHSA-w5hq-g745-h8pq
CVE: CVE-2026-41907
CWE: CWE-1285, CWE-787
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-w5hq-g745-h8pq
Type: github-advisory

## Affected
- npm: `uuid` — affected >=0 <11.1.1
- npm: `uuid` — affected >=12.0.0 <12.0.1
- npm: `uuid` — affected >=13.0.0 <13.0.1

## Details
### Summary

The `v3()`, `v5()`, and `v6()` [API methods](https://github.com/uuidjs/uuid#api-summary) (not `uuid` release versions) accept external output buffers but do not reject out-of-range writes (small `buf` or large `offset`).  
By contrast, `v4()`, `v1()`, and `v7()` API methods explicitly throw `RangeError` on invalid bounds.

This inconsistency allows **silent partial writes** into caller-provided buffers.


### Affected code

- `src/v35.ts` (`v3()`/`v5()` path) writes `buf[offset + i]` without bounds validation.
- `src/v6.ts` writes `buf[offset + i]` without bounds validation.

### Reproducible PoC

```bash
cd /home/StrawHat/uuid
npm ci
npm run build

node --input-type=module -e "
import {v4,v5,v6} from './dist-node/index.js';
const ns='6ba7b810-9dad-11d1-80b4-00c04fd430c8';
for (const [name,fn] of [
  ['v4()',()=>v4({},new Uint8Array(8),4)],
  ['v5()',()=>v5('x',ns,new Uint8Array(8),4)],
  ['v6()',()=>v6({},new Uint8Array(8),4)],
]) {
  try { fn(); console.log(name,'NO_THROW'); }
  catch(e){ console.log(name,'THREW',e.name); }
}"
```

Observed:

- `v4() THREW RangeError`
- `v5() NO_THROW`
- `v6() NO_THROW`

Example partial overwrite evidence captured during audit:

```text
same true buf [
  170, 170, 170, 170,
   75, 224, 100,  63
]
v6 [
  187, 187, 187, 187,
   31,  19, 185,  64
]
```

### Security impact

- **Primary**: integrity/robustness issue (silent partial output).
- If an application assumes full UUID writes into preallocated buffers, this can produce malformed/truncated/partially stale identifiers without error.
- In systems where caller-controlled offsets/buffer sizes are exposed indirectly, this may become a security-relevant logic flaw.

### Suggested fix

Add the same guard used by `v4()`/`v1()`/`v7()`:

```ts
if (offset < 0 || offset + 16 > buf.length) {
  throw new RangeError(`UUID byte range ${offset}:${offset + 15} is out of buffer bounds`);
}
```

Apply to:

- `src/v35.ts` (covers `v3()` and `v5()`)
- `src/v6.ts`

## References
- https://github.com/uuidjs/uuid/security/advisories/GHSA-w5hq-g745-h8pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41907
- https://github.com/uuidjs/uuid/commit/32389c887c9e75f90442ee4cc95bbab0c4e8346e
- https://github.com/uuidjs/uuid/commit/3d2c5b0342f0fcb52a5ac681c3d47c13e7444b34
- https://github.com/uuidjs/uuid/commit/3d61d6ac1f782cf6b1dd8661c60f11722cd49a0d
- https://github.com/uuidjs/uuid/commit/9d27ddf7046ce496ef39569ff84d948eeff9cb2a
- https://github.com/uuidjs/uuid
- https://github.com/uuidjs/uuid/releases/tag/v11.1.1
- https://github.com/uuidjs/uuid/releases/tag/v12.0.1
- https://github.com/uuidjs/uuid/releases/tag/v13.0.1
- https://github.com/uuidjs/uuid/releases/tag/v14.0.0
