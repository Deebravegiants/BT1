# [M] SurrealDB: Port-specific --deny-net rules silently bypassed on HTTP redirect

## Summary
Severity: Medium
Advisory: GHSA-97vg-427p-8hx5
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-97vg-427p-8hx5
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
SurrealDB offers `http::*` functions that can access external network endpoints, with the `--allow-net` and `--deny-net` capabilities used to restrict the set of network targets that can be reached. An authenticated user of SurrealDB can bypass a port-scoped `--deny-net <host>:<port>` rule by chaining an HTTP redirect: the initial request goes to an `--allow-net`-permitted hostname, the response's `3xx Location` header points at the denied `host:port`, and the redirect is followed even though the destination was explicitly denied.

The root cause is in the redirect policy applied to outbound HTTP requests (`surrealdb/core/src/fnc/util/http/mod.rs`): the `NetTarget` for the redirect destination is built from `url.host_str()` alone and `url.port()` is dropped. The capability matcher (`surrealdb/core/src/dbs/capabilities.rs:259-264`) refuses to match a port-bearing rule against a port-stripped target (`Self::Host(host, Some(port)) => match tgt { _ => false }`), so the operator's port-scoped deny rule silently does not fire on the redirect target.

### Impact

The impact of this vulnerability is circumvention of the `--deny-net` capability when the operator has scoped deny rules by port, and the resulting impact on systems external to SurrealDB. The ultimate impact is dependent on the deployment scenario.

For example, if a SurrealDB operator uses `--deny-net <host>:<port>` to block specific internal services (such as a local Redis at `192.168.1.1:6379` or an unauthenticated cloud metadata service) while leaving the rest of the host reachable, an authenticated principal that can call `http::*` and host an attacker-controlled redirect target can reach the blocked service and act on whatever interface it exposes.

Bounded to:

- Principals already permitted to call `http::*`.
- Capability configurations that scope deny rules by port. Host-only rules (`--deny-net <host>`) are not affected because the host-only rule arm of the matcher accepts port-stripped targets.

### Patches

The redirect policy now constructs the `NetTarget` for the redirect URL with `url.port()` included, so port-specific deny rules apply to redirect targets identically to initial requests.

A new integration regression test (`function_http_redirect_to_denied_port_blocked`) uses two wiremock servers to verify the redirect target is blocked and the denied server receives no requests.

Versions 3.1.0 and later are not affected.

### Workarounds

- Replace port-specific deny rules with host-only deny rules where feasible (`--deny-net 192.168.1.1` instead of `--deny-net 192.168.1.1:6379`). Host-only rules match port-stripped targets, at the cost of denying every port on that host.
- Disable `http::*` for untrusted principals (`--deny-funcs 'http::*'`) where the functions are not required.
- Terminate outbound HTTP requests at a reverse proxy that enforces port-specific access controls.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-97vg-427p-8hx5
- https://github.com/surrealdb/surrealdb/commit/https://github.com/surrealdb/surrealdb/commit/ceb1ca3a1
- https://github.com/surrealdb/surrealdb
