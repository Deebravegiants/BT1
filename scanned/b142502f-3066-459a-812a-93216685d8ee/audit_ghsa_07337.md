# [H] Woodpecker: Privilege escalation via unrestricted serviceAccountName in the Kubernetes backend

## Summary
Severity: High
Advisory: GHSA-qf34-295c-26v8
CVE: CVE-2026-61549
CWE: CWE-269, CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-qf34-295c-26v8
Type: github-advisory

## Affected
- Go: `go.woodpecker-ci.org/woodpecker/v3` — affected >=0 <3.16.0
- Go: `github.com/woodpecker-ci/woodpecker` — affected >=1.0.0
- Go: `go.woodpecker-ci.org/woodpecker/v2` — affected >=0

## Details
### Impact

A privilege escalation vulnerability affects Woodpecker instances using the **Kubernetes backend**.

The pipeline option `backend_options.kubernetes.serviceAccountName` was passed directly to the pod spec without any admin gating.

**Who is impacted:** any operator running the Kubernetes backend. Any user with **Push** permission on a connected repository can run pipeline pods under an arbitrary ServiceAccount in the pipeline namespace, gaining that account's RBAC permissions. If a privileged ServiceAccount is reachable in that namespace, this can lead to secret exfiltration (database credentials, API keys, TLS certs) and full cluster takeover.

### Patches

https://github.com/woodpecker-ci/woodpecker/pull/6792

### Workarounds

Operators who cannot upgrade immediately can mitigate by any of:

- **Restrict Push access** on repositories connected to the Kubernetes-backed instance to
  trusted users only.
- **Harden the pipeline namespace**: ensure no privileged ServiceAccount exists or is bound in
  the namespace where pipeline pods run; keep the `default` ServiceAccount minimally privileged.
- **Disable ServiceAccount token automounting** for ServiceAccounts that should not be used by
  pipelines.
- **Enforce an admission policy** (e.g. OPA/Gatekeeper, Kyverno, or a ValidatingAdmissionPolicy)
  that rejects pipeline pods setting an unexpected `serviceAccountName`.
- **Use a dedicated, isolated namespace** per org/instance with no sensitive RBAC bindings.

### Resources

- Vulnerable option introduced in commit `609ba481b5e912f59aaae8ca7bc22b44523c5e37`
- Affected versions: `v1.0.0` through `v3.15.0`
- Source: `pipeline/backend/kubernetes/backend_options.go` (field `ServiceAccountName`),
  `pipeline/backend/kubernetes/pod.go` (assigned to pod spec with no gating)

## References
- https://github.com/woodpecker-ci/woodpecker/security/advisories/GHSA-qf34-295c-26v8
- https://github.com/woodpecker-ci/woodpecker/pull/6792
- https://github.com/woodpecker-ci/woodpecker
