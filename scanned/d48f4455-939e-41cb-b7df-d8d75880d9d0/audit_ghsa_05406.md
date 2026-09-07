# [M] NocoDB has Prototype Pollution in Connection Test Endpoint, Leading to DoS

## Summary
Severity: Medium
Advisory: GHSA-95ff-46g6-6gw9
CVE: CVE-2026-24766
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-95ff-46g6-6gw9
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.0

## Details
### Summary

An authenticated user with org-level-creator permissions can exploit prototype pollution in the `/api/v2/meta/connection/test` endpoint, causing all database write operations to fail application-wide until server restart.

While the pollution technically bypasses SUPER_ADMIN authorization checks, no practical privileged actions can be performed because database operations fail immediately after pollution.

### Details

The `deepMerge()` function in `packages/nocodb/src/utils/dataUtils.ts` does not sanitize the following keys: (`__proto__`, `constructor`, `prototype`):

```typescript
export const deepMerge = (target: any, ...sources: any[]) => {
  // ...
  Object.keys(source).forEach((key) => {
    if (isMergeableObject(source[key])) {
      if (!target[key]) target[key] = Array.isArray(source[key]) ? [] : {};
      deepMerge(target[key], source[key]);  // Recursively merges __proto__
    } else {
      target[key] = source[key];
    }
  });
  // ...
};
```

The `testConnection` endpoint (`packages/nocodb/src/controllers/utils.controller.ts`) passes user-controlled input directly to `deepMerge()`:

```typescript
config = await integration.getConfig();
deepMerge(config, body);
```

When an attacker sends `{"__proto__": {"super": true}}`, the `super` property is written to `Object.prototype`, affecting all plain objects in the Node.js process.

## Impact

Pollutes Object.prototype globally, breaking all subsequent database write operations for all users until process restart.

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-95ff-46g6-6gw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-24766
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/0.301.0
