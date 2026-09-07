# [H] NodeVM network builtin exclusions bypass via internal _http_client and _http_server

## Summary
Severity: High
Advisory: GHSA-r9pm-gxmw-wv6p
CVE: CVE-2026-47139
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-r9pm-gxmw-wv6p
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
## Summary

`NodeVM` supports excluding public network builtins from the wildcard builtin option. With this configuration direct access to `http`, `https`, `http2`, `net`, `dgram`, `tls`, `dns`, and `dns/promises` is blocked.

However, Node.js also exposes underscored internal HTTP builtins such as `_http_client` and `_http_server`. These are not blocked when the public modules are excluded.

Sandboxed code can use these internal builtins to make outbound HTTP requests and open listening HTTP sockets even though the public network modules are denied.

**Note**: This is not host RCE. It is a network capability bypass that can lead to SSRF-style access to internal services.

## Details

The wildcard builtin expansion is based on Node.js builtin module names:

```js
const BUILTIN_MODULES = (nmod.builtinModules || Object.getOwnPropertyNames(process.binding('natives')))
  .filter(s=>!s.startsWith('internal/') && !DANGEROUS_BUILTINS.has(s));
```

Public modules can be excluded with `-name`:

```js
if (builtins.indexOf(`-${name}`) === -1) {
  addDefaultBuiltin(res, name, hostRequire);
}
```

But excluding `http` and `net` does not exclude internal siblings such as:

```text
_http_client
_http_server
_tls_wrap
```

These internal modules expose network primitives.

Confirmed examples:

1. `require('_http_client').ClientRequest(...)` performs an outbound HTTP request to a host-local service while `http` and `net` are blocked.
2. `require('_http_server').Server(...).listen(...)` opens a listening HTTP socket while `http` and `net` are blocked.

## PoC

Tested on:

```text
vm2: 3.11.2
Node.js: v25.9.0
```

Run from the vm2 repository root:

```bash
node poc/internal-http-builtin-network-bypass.js
```
[internal-http-builtin-network-bypass.js](https://github.com/user-attachments/files/27571182/internal-http-builtin-network-bypass.js)


The PoC first confirms the intended restrictions work then bypasses them:

```text
require("_http_client").ClientRequest(...)
```

This performs an HTTP request to a host-local service and reads the response.

It also confirms:

```text
require("_http_server").Server(...).listen(0)
```

This opens a listening HTTP socket from inside the sandbox.

<img width="951" height="623" alt="Screenshot 2026-05-10 at 1 07 39 PM" src="https://github.com/user-attachments/assets/21bfb1ff-dd15-423a-92c4-0337cd07816c" />

## Impact

An attacker who can run untrusted JavaScript inside `NodeVM` with this affected builtin configuration can regain network access even when the application attempted to block network modules.

This can allow SSRF-style access to localhost services, metadata endpoints, internal admin panels, or other network resources reachable from the host process.

## Suggested fix

Treat underscored internal network modules as dangerous or link their availability to the public module they wrap.

At minimum, exclude related internal modules such as:

```text
_http_agent
_http_client
_http_common
_http_incoming
_http_outgoing
_http_server
_tls_common
_tls_wrap
```

Alternatively, deny underscored Node.js internals from wildcard builtin expansion by default.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-r9pm-gxmw-wv6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-47139
- https://github.com/patriksimek/vm2/commit/436053e30eecbabd487e2fd2959c137ac34e2bb1
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
