# [M] Deno: Node TCPWrap numeric hostname aliases bypass --deny-net resolved-IP deny checks

## Summary
Severity: Medium
Advisory: GHSA-v8fw-85r8-5m23
CVE: CVE-2026-49411
CWE: CWE-284
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-v8fw-85r8-5m23
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.8.0

## Details
## Summary

Deno's network permission model is designed so that `--deny-net` rules apply to the **resolved IP address** of a destination, not just the literal string supplied by the caller. That means `--deny-net=127.0.0.1` (or `--deny-net=127.0.0.0/8`) is expected to block any attempt to reach loopback, regardless of how the hostname is spelled.

On affected versions, the Node.js compatibility TCP path checked the permission against the **original hostname string** before resolution and then did not re-check after resolution. A caller could therefore pass a numeric alias of an IP address (for example the decimal integer `2130706433` or the hex form `0x7f000001`, both of which resolve to `127.0.0.1`) and reach the denied destination through `node:net.connect` or `node:http.request`'s `{ host, port }` options form.

The native `Deno.connect()`, `fetch()`, and URL-string variants of `node:http.request("http://...")` were not affected, because they either re-checked permissions after resolution or normalized the hostname through the URL parser before checking.

## Proof of concept

Run on Deno `2.7.14`, with a local TCP listener on `127.0.0.1:<PORT>`:

```js
import net from "node:net";

// --allow-net + --deny-net=127.0.0.0/8
// (or even --deny-net=127.0.0.1:<PORT>)
net.connect({ host: "2130706433", port: PORT });     // CONNECTED ❌
net.connect({ host: "0x7f000001", port: PORT });     // CONNECTED ❌
net.connect({ host: "127.0.0.1",  port: PORT });     // denied ✅
```

The same primitive reached the loopback HTTP listener through `node:http` when the destination was passed as options rather than as a URL string:

```js
import http from "node:http";

// options-form host — bypasses the deny rule on affected versions
http.request({ hostname: "2130706433", port: PORT, path: "/" }).end();

// URL-string form — correctly denied (URL parser normalizes the host)
http.request(`http://2130706433:${PORT}/`).end();
```

The server-side log showed the bypassed requests arriving from `127.0.0.1` with the numeric alias preserved in the `Host` header.

## Impact

A program that intentionally allows broad outbound network access but uses `--deny-net` to carve out protected destinations, typically loopback, private/internal ranges, or cloud-instance metadata IPs, could be made to reach those denied destinations from less-trusted code (a dependency, plugin, or attacker-controlled input) that funnels through `node:net.connect({ host })` or `node:http.request({ hostname })`.

The CVSS vector reflects this as a local-attack-vector, permissions-required confidentiality impact: the attacker needs to be able to run code inside the Deno process, and the demonstrated primitive is "reach an explicitly denied IP." It does not by itself exfiltrate data or execute code; the further impact depends on what the now-reachable endpoint exposes.

The confirmed scope is **IPv4 numeric hostname aliases** reaching a denied resolved IP through the Node TCPWrap / options-host path. URL strings, `node:http2`, `undici`, and IPv6 numeric/mapped-address variants were not exhaustively tested by the reporter.

## Not affected

- Programs that do not use `--deny-net` at all (the bug is specifically about deny rules being bypassed; allow rules were always checked against the original string).
- Native Deno networking APIs (`Deno.connect`, `Deno.connectTls`, `fetch`, ...), these already re-checked permissions after resolution as of PR #33203.
- URL-string callers such as `fetch("http://2130706433/")` or `node:http.request("http://2130706433/")`, the URL parser normalized the hostname to its dotted-quad form before the   permission check ran.
- Calls that do not provide `host`/`hostname` (e.g. connecting by IP literal or by a name that the deny rule already matches verbatim).

## Workarounds

If you cannot upgrade immediately, reduce exposure by:

- **Preferring an `--allow-net` allowlist over a `--deny-net` denylist.** An allowlist denies numeric aliases by default because they don't match the listed hostnames; only the destinations you've explicitly permitted can be reached.
- **Validating untrusted host input** before passing it to `node:net.connect` / `node:http.request`. Reject hostnames that are purely decimal integers (`/^\d+$/`) or begin with `0x`, as these are the alias forms exploited by the bypass.
- **Avoiding the Node options-host path for sensitive calls** in favour of URL-string forms, which are normalized by the URL parser before the permission check.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-v8fw-85r8-5m23
- https://nvd.nist.gov/vuln/detail/CVE-2026-49411
- https://github.com/denoland/deno
