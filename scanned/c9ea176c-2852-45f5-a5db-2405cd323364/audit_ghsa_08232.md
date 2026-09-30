# [H] Fission StorageSvc /v1/archive endpoint exposes unauthenticated CRUD over all function archives

## Summary
Severity: High
Advisory: GHSA-chf8-4hv6-8pg6
CVE: CVE-2026-46612
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-chf8-4hv6-8pg6
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.23.0

## Details
### Summary

The Fission `storagesvc` component registers archive CRUD handlers (`/v1/archive` GET / POST / DELETE and `/v1/archives` list) directly on its HTTP router without performing any authentication or authorization. Any caller able to reach the `storagesvc` ClusterIP — including  any other workload in the same Kubernetes cluster — could enumerate archive IDs, download archives belonging to other tenants, upload arbitrary archive content, and delete archives.

 ### Affected component

  - `pkg/storagesvc/storagesvc.go` — handler registration and per-route handler logic at lines   72-95 (list), 167-199 (download/delete), and 263-270 (route wiring).

 ### Impact

A workload elsewhere in the cluster (e.g. a compromised function pod, a noisy-neighbour tenant in a multi-tenant deployment, or any pod whose egress is not constrained by NetworkPolicy) could:

  1. Enumerate every function deployment archive in the cluster.
  2. Download the deployment archive of any function in any namespace, exposing the function's source code and any embedded secrets.
  3. Delete archives, causing the next function specialization or rebuild to fail.
  4. Upload arbitrary archives that subsequent function specializations would fetch and execute.

In multi-tenant Fission deployments this completely breaks the tenant boundary for function code.

  ### Root cause

`pkg/storagesvc/storagesvc.go` mounts the handlers without an authentication middleware. Network-layer controls (`NetworkPolicy`) were the only line of defence before this fix, and the chart shipped no `NetworkPolicy` for `storagesvc` by default, so reachability was open.

  ### Fix

  Released in [v1.23.0](https://github.com/fission/fission/releases/tag/v1.23.0):

  - **PR #3368** (commit `2455fc0c`) wraps the `storagesvc` archive routes with the application-layer HMAC verifier from `pkg/auth/hmac` using the `ServiceStoragesvc` derived key. Callers (executor, fetcher, builder, CLI) sign their requests using a shared cluster master secret derived per-service via HKDF. Mismatched signatures are rejected with `401`.
  - Defence in depth: **PR #3365** added a `NetworkPolicy` for `storagesvc` so only the executor/fetcher/builder pods can reach it network-layer (independent of authentication).

  ### Mitigation (until upgrade)

  1. Enable the Helm chart's per-service NetworkPolicy (set `networkPolicy.enabled=true`).
  2. Restrict `storagesvc` egress/ingress to the executor, builder, and fetcher pods only.
  3. Avoid running untrusted workloads in the cluster that hosts Fission.

## References
- https://github.com/fission/fission/security/advisories/GHSA-chf8-4hv6-8pg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-46612
- https://github.com/fission/fission/pull/3365
- https://github.com/fission/fission/pull/3368
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.23.0
