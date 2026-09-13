# [M] Budibase: CouchDB Reduce Injection via Unsanitized Calculation Parameter in V1 Views API 

## Summary
Severity: Medium
Advisory: GHSA-363w-hvwh-w7m6
CVE: CVE-2026-45719
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-363w-hvwh-w7m6
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.38.1

## Details
# Security Advisory: CouchDB Reduce Injection via Unsanitized Calculation Parameter in V1 Views API

**Affected Software:** Budibase
**Affected Component:** `packages/server/src/api/controllers/view/viewBuilder.ts`, `packages/server/src/api/routes/view.ts`
**CWE:** CWE-94 (Improper Control of Generation of Code)
**Discovery Date:** 2026-03-24

---

## Summary

The V1 Views API (`POST /api/views`) accepts a `calculation` parameter from the request body that is interpolated directly into a CouchDB reduce function definition without validation. Although an internal `SCHEMA_MAP` object defines the valid calculation types (`sum`, `count`, `stats`), no actual validation is performed against this map before the value is used in string interpolation.

A user with Builder permissions can inject arbitrary JavaScript code that will be executed within the CouchDB JavaScript engine when the view is queried.

---

## Affected Component

**Route:** `POST /api/views` (V1 legacy views endpoint)
**File:** `packages/server/src/api/routes/view.ts`, line 45

```js
.post("/api/views", viewController.v1.save)
```

Note: This route has no Joi request body validator, unlike the V2 views endpoint which uses `viewValidator()`.

**Vulnerable code:** `packages/server/src/api/controllers/view/viewBuilder.ts`, line 213

```js
const reduction = field && calculation ? { reduce: `_${calculation}` } : {}

return {
  meta: { field, tableId, groupBy, filters, schema, calculation, ... },
  map: `function (doc) { ... }`,
  ...reduction,    // <-- unvalidated calculation string becomes CouchDB reduce
}
```

---

## Vulnerability Detail

The `viewBuilder` function constructs a CouchDB design document view definition. It correctly sanitizes all inputs that flow into the `map` function string (using `JSON.stringify` for field names and a strict `TOKEN_MAP` allowlist for filter operators).

However, the `calculation` parameter follows a different path:

1. User submits `calculation` via `POST /api/views` request body
2. No Joi validator is present on this V1 route
3. `viewBuilder` receives `calculation` as a raw string
4. It is interpolated as: `` reduce: `_${calculation}` ``
5. This reduce definition is saved to a CouchDB design document
6. When the view is queried, CouchDB evaluates the reduce value

CouchDB's behavior for reduce functions:
- Values starting with `_` followed by a known built-in (`_sum`, `_count`, `_stats`) are executed as native reducers
- Any other value is treated as a **JavaScript function string** and executed in CouchDB's SpiderMonkey JS engine

The `SCHEMA_MAP` object in the same file defines `sum`, `count`, and `stats` as valid keys, but this map is only used for schema construction — it is never used as an input validator for the `calculation` parameter.

---

## Steps to Reproduce

**Prerequisites:** Authenticated session with Builder role permissions.

**1. Send a crafted view creation request:**

```bash
curl -X POST https://<budibase-instance>/api/views \
  -H "Content-Type: application/json" \
  -H "Cookie: <builder-session-cookie>" \
  -d '{
    "name": "test_view",
    "tableId": "<valid-table-id>",
    "field": "amount",
    "calculation": "stats\"); } function(keys,values,rereduce){ var data = \"\"; for(var i in this) { data += i + \"=\" + this[i] + \",\"; } return data; } //"
  }'
```

**2. Query the created view:**

```bash
curl https://<budibase-instance>/api/views/test_view?group=true \
  -H "Cookie: <builder-session-cookie>"
```

**3. Expected result:** The injected JavaScript function executes in CouchDB's JS context during reduce evaluation. The function can:
- Enumerate objects available in the CouchDB sandbox
- Access document data from the reduce `values` parameter
- Return arbitrary data in the view response

**Simplified test:** To verify the injection point without complex payloads:

```json
{
  "name": "calc_test",
  "tableId": "<valid-table-id>",
  "field": "amount",
  "calculation": "INVALID_NOT_A_BUILTIN"
}
```

This produces `reduce: "_INVALID_NOT_A_BUILTIN"`. CouchDB will reject this as neither a valid built-in nor a valid function, confirming that arbitrary strings reach the reduce evaluator.

---

## Impact

- **Code execution:** Arbitrary JavaScript runs in CouchDB's SpiderMonkey sandbox
- **Data access:** The reduce function receives all matching document values, allowing data exfiltration across the database
- **Scope limitation:** CouchDB's JS sandbox prevents filesystem or network access — this is not OS-level RCE
- **Authentication required:** Attacker must have Builder role, which already grants significant application access
- **Persistence:** The injected reduce function persists in the design document and executes on every view query

---

## Recommended Fix

Add an allowlist validation in `viewBuilder` before the reduce interpolation:

```typescript
const VALID_CALCULATIONS = ["sum", "count", "stats"];

if (calculation && !VALID_CALCULATIONS.includes(calculation)) {
  throw new Error(`Invalid calculation type: ${calculation}`);
}

const reduction = field && calculation ? { reduce: `_${calculation}` } : {};
```

Additionally, add a Joi validator to the V1 views route to match the V2 endpoint:

```typescript
// In packages/server/src/api/routes/view.ts
.post("/api/views", v1ViewValidator(), viewController.v1.save)
```

---

## Additional Context

The V2 views API (`POST /api/v2/views`) uses `viewValidator()` with Joi schema validation and a separate calculation handling path. This finding is specific to the V1 legacy endpoint which lacks equivalent input validation.

The `map` function string in the same code is properly protected — all user inputs reaching it are escaped via `JSON.stringify()` or validated against a strict `TOKEN_MAP` allowlist. Only the `reduce` path is affected.

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-363w-hvwh-w7m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45719
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.38.1
