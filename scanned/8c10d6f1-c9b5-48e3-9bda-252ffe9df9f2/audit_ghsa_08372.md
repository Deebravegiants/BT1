# [M] NodeVM observability builtins leak host process and HTTP request data

## Summary
Severity: Medium
Advisory: GHSA-9g8x-92q2-p28f
CVE: CVE-2026-47141
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-9g8x-92q2-p28f
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
## Summary

`NodeVM` exposes some process-wide observability builtins when they are allowed through `require.builtin`.

The following builtins are not blocked by the dangerous builtin denylist:

```text
diagnostics_channel
async_hooks
perf_hooks
```

These modules are process-wide, not sandbox-local. Sandboxed code can use them to observe host application data across the vm2 boundary.

**Note**: It is a host data exposure issue. The impact depends on whether the host application allows these builtins and uses HTTP, async request context, diagnostics channels, or performance marks in the same process.

## Details

Non-denied builtins are exposed to the sandbox through `lib/builtin.js`:

```js
builtins.set(key, special ? special : vm => vm.readonly(hostRequire(key)));
```

`diagnostics_channel`, `async_hooks`, and `perf_hooks` are not denied. These modules expose host process state rather than sandbox-local state.

Confirmed examples:

1. `diagnostics_channel` lets sandboxed code subscribe to Node.js HTTP diagnostic channels such as `http.server.request.start`. The sandbox receives host HTTP request objects and can read headers such as `Authorization` or session tokens.
2. `async_hooks.executionAsyncResource()` lets sandboxed code read the current host `AsyncResource`. If the host stores request/user data on that resource, the sandbox can read it.
3. `perf_hooks.performance.getEntriesByType('mark')` lets sandboxed code read host performance timeline entries.

## PoC

Run from the vm2 repository root:

```bash
node poc/observability-builtins-info-leak.js
```
[observability-builtins-info-leak.js](https://github.com/user-attachments/files/27571259/observability-builtins-info-leak.js)

The PoC uses only the specific builtin being tested in each section.

It confirms:

```text
diagnostics_channel: sandbox reads host HTTP request headers
async_hooks: sandbox reads host AsyncResource data
perf_hooks: sandbox reads host performance mark names
```

Example impact from the PoC:

```text
authorization: Bearer HOST_HTTP_SECRET_...
x-session-token: HOST_HTTP_SECRET_...
```

These values are sent to a host HTTP server, but the sandbox reads them through `diagnostics_channel`.

<img width="997" height="566" alt="Screenshot 2026-05-10 at 1 13 20 PM" src="https://github.com/user-attachments/assets/36a7d600-8b53-4bfe-ab06-4e6dcfad5015" />

## Impact

An attacker who can run untrusted JavaScript inside `NodeVM` with affected builtin settings can observe data from the host process.

In a real application, this may expose HTTP request headers, authorization tokens, session tokens, request context values, user identifiers, or other sensitive diagnostics data from the host application or from other users.

## Suggested fix

Treat process-wide observability modules as dangerous builtins for untrusted sandboxes.

At minimum, consider blocking:

```text
diagnostics_channel
async_hooks
perf_hooks
```

These modules are not sandbox-local and can expose host process state across the vm2 boundary.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-9g8x-92q2-p28f
- https://nvd.nist.gov/vuln/detail/CVE-2026-47141
- https://github.com/patriksimek/vm2/commit/e1c48fce05189f48e71efbd32af0754efa4066bb
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
