# [C] Fission router exposes /fission-function/<ns>/<name> on its public listener, allowing invocation of any function without an HTTPTrigger

## Summary
Severity: Critical
Advisory: GHSA-3g33-6vg6-27m8
CVE: CVE-2026-46614
CWE: CWE-284, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-3g33-6vg6-27m8
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.23.0

## Details
### Summary

The Fission router registers an internal-style route — `/fission-function/<name>` and `/fission-function/<ns>/<name>` — for every `Function` object, independent of whether any `HTTPTrigger` exists for that function. The route was mounted on the same listener as user-defined `HTTPTrigger`s (`svc/router`, port 8888), so any caller who could reach the router could invoke any function by guessing its `metadata.name` (and namespace), bypassing the host / path / method / method-allow-list restrictions encoded in `HTTPTrigger` objects.

### Affected component

- `pkg/router/httpTriggers.go:280-284` — `internalRoute` registration via `utils.UrlForFunction(fn.Name, fn.Namespace)`, bound to the function handler.

### Impact

An external caller who reaches the public router could:

1. Invoke functions that the operator intentionally did not publish through an `HTTPTrigger` (e.g. functions used only as Kubewatcher / Timer / MessageQueue trigger targets, internal helpers, or sample functions).
2. Bypass `HTTPTrigger`-level restrictions: a function published only on `POST /api/v2/foo` could still be invoked as `GET /fission-function/<ns>/<name>` with arbitrary headers and body.
3. Enumerate function names by probing the response semantics (404 vs 200 vs 502 from cold start).

In multi-tenant deployments this also crosses tenant boundaries when functions in tenant namespace B are reachable from tenant A's pods (or from anywhere on the internet if the router is ingress-exposed).

### Root cause

`/fission-function/...` was historically used by internal trigger sources (timer, kubewatcher, mqtrigger) that share the cluster network with the router, but the route was registered on the public listener that also serves user `HTTPTrigger`s. The two audiences were never separated.

### Fix

Released in [v1.23.0](https://github.com/fission/fission/releases/tag/v1.23.0):

- **PR #3369** (commit `814d232c`): the router now runs **two** listeners — a public listener (port 8888, `svc/router`) that serves only user-defined `HTTPTrigger`s, `/router-healthz`, and `/_version`, and an internal listener (port 8889, `svc/router-internal`, ClusterIP-only) that exclusively serves `/fission-function/<ns>/<name>`. The internal listener is wrapped with the `pkg/auth/hmac.ServiceVerifier` using the `ServiceRouterInternal` derived key — internal trigger sources sign their requests with a per-service HKDF-derived key from a cluster master secret. Empty master secret falls back to pass-through (preserves compatibility for clusters not yet rotating in a secret).
- **PR #3365** (commit `0aa24788`): added per-service `NetworkPolicy` resources to `charts/fission-all`, ensuring `svc/router-internal` is only reachable from `kubewatcher`, `timer`, `mqtrigger`, and `mqt-keda` pods inside the release namespace.
- The internal-listener path itself is still **`/fission-function/<ns>/<name>`** — only its location moved.

### Mitigation (until upgrade)

1. Apply a `NetworkPolicy` to the Fission namespace that allows ingress to `svc/router` (port 8888) only from the consuming project's ingress controller, and blocks `/fission-function/...` at the ingress layer (path-based filter on the ingress).
2. Avoid exposing the router directly via LoadBalancer/NodePort; front it with an ingress that path-filters `/fission-function/`.
3. Treat function `metadata.name` as **not** a secret — names should not be the access control boundary.

## References
- https://github.com/fission/fission/security/advisories/GHSA-3g33-6vg6-27m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-46614
- https://github.com/fission/fission/pull/3365
- https://github.com/fission/fission/pull/3369
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.23.0
