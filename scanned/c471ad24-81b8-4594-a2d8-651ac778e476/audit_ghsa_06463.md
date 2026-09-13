# [M] Fission: HTTPTrigger admission omits RelativeURL / Prefix validation; kubectl apply bypasses CLI checks

## Summary
Severity: Medium
Advisory: GHSA-vchh-r53j-8mpw
CVE: CVE-2026-50569
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-vchh-r53j-8mpw
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.25.0

## Details
`HTTPTriggerSpec.Validate()` validated `Methods`, `FunctionReference`, `Host`, `IngressConfig`, and `CorsConfig`, but silently skipped `RelativeURL` and `Prefix`. Those two fields were validated at the CLI level only
(`pkg/fission-cli/cmd/httptrigger/create.go:83`). The post-CRD-modernization webhook for HTTPTrigger was retired in favor of API-server CEL — and CEL had no rules on those fields either — so an HTTPTrigger created via `kubectl apply` or
a direct Kubernetes REST API call bypassed every URL-level check.

A tenant with HTTPTrigger create permission could therefore create triggers whose `RelativeURL` or `Prefix`:

- was empty (with both fields unset, the trigger has no URL),
- did not start with `/`,
- was exactly `/` (claiming the entire router root),
- contained `..` traversal segments (e.g. `/api/../admin`),
- collided with router-owned routes: `/router-healthz`, `/readyz`, `/_version`, `/auth/login`,
- collided with the router-internal function prefix `/fission-function/<ns>/<name>`.

### Affected

- Project: `github.com/fission/fission`
- Versions: all versions through v1.24.0
- Audited commit: `647c141`
- Component: `pkg/apis/core/v1/validation.go:HTTPTriggerSpec.Validate` (and the missing CEL on `HTTPTriggerSpec`)
- Configuration: default

Fix section (paste into the Fix / Patches field)

Fixed in [v1.25.0](https://github.com/fission/fission/releases/tag/v1.25.0) by:

- [PR #3464](https://github.com/fission/fission/pull/3464) (commit [`0deed6bf`](https://github.com/fission/fission/commit/0deed6bf2af2a0c0c6094b25e1a0afad36773e3b)) — enforce the path-safety invariants at both admission layers so the API
server's CEL evaluation and the Go-side `HTTPTriggerSpec.Validate()` agree:
  - Three `+kubebuilder:validation:XValidation` rules on `HTTPTriggerSpec` (the API server's CEL admission gate, regenerated into `crds/v1/fission.io_httptriggers.yaml`):
    - at least one of `relativeurl` or `prefix` must be non-empty;
    - `relativeurl`, when set, must start with `/`, must not be `/`, must contain no `..` segment, must not be in the reserved exact-path set, and must not start with `/fission-function/`;
    - `prefix`, when set, the same rules guarded by `has(self.prefix)`.
  - `validateTriggerPath` helper in `pkg/apis/core/v1/validation.go`, invoked from `HTTPTriggerSpec.Validate()`, mirrors the CEL rules so the CLI's early rejection and the router reconciler's status-Condition path match what the API
server admits.

Regression coverage: a new `TestHTTPTriggerSpecValidate_Path` table in `pkg/apis/core/v1/validation_validators_test.go` exercises every PoC case from the advisory plus literal `..`-prefixed-segment positives that must remain allowed.

## References
- https://github.com/fission/fission/security/advisories/GHSA-vchh-r53j-8mpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-50569
- https://github.com/fission/fission/pull/3464
- https://github.com/fission/fission/commit/0deed6bf3f26bc0f10e9130cd0d479b0b9f5f609
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.25.0
