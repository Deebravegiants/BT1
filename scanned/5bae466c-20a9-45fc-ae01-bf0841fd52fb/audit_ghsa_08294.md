# [H] @rvf/set-get has a prototype pollution issue that's reachable via @rvf/core preprocessFormData (HTTP form data)

## Summary
Severity: High
Advisory: GHSA-c567-44rc-m5hq
CVE: CVE-2026-44483
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-c567-44rc-m5hq
Type: github-advisory

## Affected
- npm: `@rvf/set-get` — affected >=7.0.0 <7.0.2
- npm: `@rvf/set-get` — affected >=6.0.0 <6.0.4

## Details
## Summary

`setPath` in `@rvf/set-get` (used by `@rvf/core` to flatten incoming form data into a nested object) does not block the keys `__proto__`, `constructor`, or `prototype` when walking a path. Because field names in submitted form data are passed directly to `setPath` via `preprocessFormData` (and through `parseFormData` / `validate`), an attacker who can submit a form to a Remix / React Router app using the library can set arbitrary properties on `Object.prototype` of the running server process.

This is a default-reachable prototype pollution primitive: no special configuration is required. Any endpoint that accepts a form via `parseFormData` or runs a validator created with `createValidator` is affected.

## Affected versions

- `@rvf/set-get` `< 7.0.2` (7.x line)
- `@rvf/set-get` `< 6.0.4` (6.x line)

Reached through `@rvf/core` versions that depend on a vulnerable `@rvf/set-get` (current `8.1.0` resolves to `7.0.1` without the override).

## Patched

- `@rvf/set-get` `7.0.2`
- `@rvf/set-get` `6.0.4`

The fix adds a `REJECT_KEYS` blocklist (`__proto__`, `constructor`, `prototype`) and throws when one is encountered while walking a path inside `setPath`.

## Proof of concept

Install a vulnerable resolution and run on Node 18+:

```json
{
  "dependencies": { "@rvf/core": "8.1.0" },
  "overrides": { "@rvf/set-get": "7.0.1" }
}
```

```js
const { preprocessFormData } = require('@rvf/core');

const form = new FormData();
form.append("username", "alice");
form.append("__proto__[polluted]", "yes");

preprocessFormData(form);
console.log(({}).polluted); // -> 'yes'
```

The field name `__proto__[polluted]` is the kind of value an attacker can submit from any HTML form or HTTP client. After the call, every plain object in the process inherits `polluted = 'yes'`.

A second working payload is `constructor.prototype.<key>=<value>`, which goes through `setPath` walking `constructor` then `prototype`.

## Impact

- Any property assignable on `Object.prototype` of the server process, set by a single unauthenticated HTTP request.
- Persists for the life of the worker process and affects every subsequent request handled by the same process.
- Direct downstream consequences depend on the host application and the rest of its dependency tree, but typical risks include: bypassing `if (obj.isAdmin)` style checks, injecting unintended config values into objects merged with user input, breaking template rendering, and crashing the worker by polluting properties used by other libraries (DoS).
- Worth noting: the visible output of `preprocessFormData` does not contain the malicious key, so the attack leaves no obvious trace in request logs that show parsed bodies.

## CVSS

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L` (8.2, High)

Integrity is High because the primitive lets the attacker change the meaning of property reads on every object in the process. Confidentiality is None and Availability is Low without a named downstream gadget; both could be higher in a specific consuming app.

## Remediation for users

Upgrade to `@rvf/set-get` `7.0.2` or `6.0.4`. If you cannot upgrade `@rvf/core` directly, an `npm` / `pnpm` override on `@rvf/set-get` works.

## Credit

Reported by Mohamed Bassia (@0xBassia).

## References
- https://github.com/airjp73/rvf/security/advisories/GHSA-c567-44rc-m5hq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44483
- https://github.com/airjp73/rvf
