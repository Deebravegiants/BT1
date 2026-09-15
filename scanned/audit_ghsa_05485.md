# [H] Mass Assignment in AdonisJS Lucid Allows Overwriting Internal ORM State

## Summary
Severity: High
Advisory: GHSA-g5gc-h5hp-555f
CVE: CVE-2026-22814
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-g5gc-h5hp-555f
Type: github-advisory

## Affected
- npm: `@adonisjs/lucid` — affected >=0 <21.8.2
- npm: `@adonisjs/lucid` — affected >=22.0.0-next.0 <22.0.0-next.6

## Details
### Summary
**Description**
A Mass Assignment (CWE-915) vulnerability in AdonisJS Lucid may allow a remote attacker who can influence data that is passed into Lucid model assignments to overwrite the internal ORM state. This may lead to logic bypasses and unauthorized record modification within a table or model. This affects @adonisjs/lucid through version 21.8.1 and 22.x pre-release versions prior to 22.0.0-next.6. This has been patched in @adonisjs/lucid versions 21.8.2 and 22.0.0-next.6.

### Details
A vulnerability in the `BaseModelImpl` class of `@adonisjs/lucid` may allow an attacker to overwrite internal class properties (such as `$isPersisted`, `$attributes`, or `$isDeleted`) when passing plain objects to model assignment methods.

The library relies on a `this.hasOwnProperty(key)` check to validate assignment targets. However, because internal ORM state properties are initialized as instance properties, they pass this check. Consequently, if an attacker can influence specific keys (like `$isPersisted`) into the payload passed to `merge()` or `$consumeAdapterResult()`, they can hijack the ORM's internal logic.

The exposed internal properties include:
- `$attributes`: The raw storage for model data.
- `$isPersisted`: Controls whether `save()` performs an `INSERT` or an `UPDATE`.
- `$original`: Stores the original state of the record used to calculate changes.
- `$isDeleted`: Prevents operations on deleted models.

This issue propagates to the entire write surface of the library, including:
- Instance methods `fill` and  `merge`.
- Single record creation methods `create`, `createQuietly`, `firstOrNew`, and `firstOrCreate`.
- Conditional updates via `updateOrCreate`.
- Bulk operations `createMany`, `createManyQuietly`, `fetchOrNewUpMany`, `fetchOrCreateMany`, and `updateOrCreateMany`.

### Impact
Applications are vulnerable if they pass unvalidated data or validated data that retains unknown properties to the model. This occurs because internal keys exist as instance properties, causing them to pass the `hasOwnProperty` check and bypass Lucid's default rejection of unknown properties.

Applications utilizing strict allow lists for input validation that discard unknown properties are not affected.

For example, if a developer passes `request.all()`, `request.except()` or a schema with `allowUnknownProperties` to `Model.create()`, the ORM's internal logic can be hijacked. Because the `Model.create()` > `save()` decision is based on `$isPersisted`, and `merge()` can assign to the own-property `$isPersisted`, an attacker who can inject `"$isPersisted": true` into the payload can force `save()` to take the UPDATE branch rather than the INSERT branch, while setting `$attributes` can bypass validators or field restrictions.


### Patches
This issue has been patched in @adonisjs/lucid version `21.8.2` and `22.0.0-next.6`. Please upgrade to this version or later.

Developers can mitigate this issue by strictly validating model inputs with an allow list that drops unknown keys if possible.

## References
- https://github.com/adonisjs/lucid/security/advisories/GHSA-g5gc-h5hp-555f
- https://nvd.nist.gov/vuln/detail/CVE-2026-22814
- https://github.com/adonisjs/lucid
