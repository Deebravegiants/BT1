# [H] n8n's Unsafe Buffer Allocation Allows In-Process Memory Disclosure in Task Runner

## Summary
Severity: High
Advisory: GHSA-49mx-fj45-q3p6
CVE: CVE-2025-61917
CWE: CWE-200, CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-49mx-fj45-q3p6
Type: github-advisory

## Affected
- npm: `n8n` — affected >=1.65.0 <1.114.3

## Details
### Impact

The use of `Buffer.allocUnsafe()` and `Buffer.allocUnsafeSlow()` in the task runner allowed untrusted code to allocate uninitialized memory. Such uninitialized buffers could contain residual data from within the same Node.js process (for example, data from prior requests, tasks, secrets, or tokens), resulting in potential information disclosure.  

Only authenticated users are able to execute code through Task Runners.

This issue affected any deployment in which both of the following conditions were met:
- Task Runners were enabled using `N8N_RUNNERS_ENABLED=true` (default: false)
- Code Node was enabled (default: true)


### Patches

Access to unsafe Buffer functions has been removed from the task runner sandbox. All buffer allocations are now zero-filled by default.

- **Fixed in:** 1.114.3 & 1.115.0
- **Action:** It is strongly recommended to upgrade to version ≥ 1.114.3 as soon as possible.

Changes introduced in this patch include:
- Routing all buffer allocations through `Buffer.alloc` (which zero-fills) operations where applicable  
- Adding regression tests to ensure continued enforcement of safe allocation practices


### Workarounds

If an immediate upgrade cannot be applied, the following hardening steps are recommended:

- Disable the Code Node by adding `n8n-nodes-base.code` to the `NODES_EXCLUDE` environment variable  
- Prefer external mode for isolation: run Task Runners in external mode so that untrusted task code executes in a separate sidecar container rather than within the main n8n process. This configuration significantly reduces the risk of in-process memory disclosure caused by unsafe buffer allocations.  
  In external mode, a launcher manages Task Runner processes in a dedicated sidecar environment, separate from the primary n8n instance.  
  See the [n8n documentation](https://docs.n8n.io/hosting/configuration/task-runners/) for configuration details and required environment variables.


### Resources

- Node.js documentation: [`Buffer.alloc()`](https://nodejs.org/docs/latest-v22.x/api/buffer.html#static-method-bufferallocsize-fill-encoding) vs [`Buffer.allocUnsafe()`](https://nodejs.org/docs/latest-v22.x/api/buffer.html#static-method-bufferallocunsafesize) — background on zero-filled vs uninitialized allocations  
- [n8n Documentation — Task Runners](https://docs.n8n.io/hosting/configuration/task-runners/) — external mode, setup guide, and environment configuration details
- [n8n Documentation — Blocking nodes](https://docs.n8n.io/hosting/securing/blocking-nodes/) — how to globally disable specific nodes

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-49mx-fj45-q3p6
- https://nvd.nist.gov/vuln/detail/CVE-2025-61917
- https://github.com/n8n-io/n8n/commit/2c4c2953199733c791f739a40879ae31ca129aba
- https://github.com/n8n-io/n8n
