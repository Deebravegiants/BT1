# [C] Envoy Gateway: Authentication Bypass via Improper Input Validation in EnvoyExtensionPolicy Lua Allows Secret Disclosure

## Summary
Severity: Critical
Advisory: GHSA-wcrf-9vrr-854f
CVE: CVE-2026-53713
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-wcrf-9vrr-854f
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
### Impact

The `to_absolute_normalized_path` function (security.lua:28-43) does not collapse redundant path separators (// → /). On Linux, `//etc/passwd` is equivalent to `/etc/passwd` (POSIX path semantics), but `is_critical_path` fails to match the double-slash variant because `//etc/passwd` does not start with `/etc/`.

This allows Lua code submitted as an `EnvoyExtensionPolicy` to read arbitrary files from the gateway controller pod's filesystem during Strict validation (the default), including:

* `/etc/passwd`
* Kubernetes SA tokens via `//var/run/secrets/kubernetes.io/serviceaccount/token`
* TLS certificates via `//certs/...`
* Process environment via `//proc/self/environ`

These credentials can be used to read sensitive information from the K8s API Server or from the Gateway XDS server.

### Patches

This has been patched in versions >= v1.7.4 and v1.8.1

  - Collapse redundant path separators (`//` to `/`) so double-slash variants like `//etc/passwd` and `//var/run/secrets/...` are matched by the critical-path check.
  - Rewrite the traversal check to reject any `.` or `..` segment in any position and across both separator styles (catches `/etc/./passwd`, `./etc/passwd`, `/etc/.`).

### Workarounds
Please refer to the `Warning` section in [Lua docs](https://gateway.envoyproxy.io/v1.8/tasks/extensibility/lua/) for measures to reduce risk.

### Credits

Envoy Gateway thanks @dashingDragon and @Donjon-Cerberus for reporting this issue.

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-wcrf-9vrr-854f
- https://github.com/envoyproxy/gateway
