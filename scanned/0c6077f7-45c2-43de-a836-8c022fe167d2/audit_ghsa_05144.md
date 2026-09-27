# [H] Fission: Cross-namespace Environment reference via unvalidated EnvironmentRef in Function admission webhook

## Summary
Severity: High
Advisory: GHSA-cvw6-gfvv-953q
CVE: CVE-2026-49824
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-cvw6-gfvv-953q
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

The Fission Function admission webhook (`pkg/webhook/function.go`) validated that `spec.secrets[].namespace` and `spec.configmaps[].namespace` equalled the function's own namespace but performed no equivalent check on
`spec.environment.namespace`.

### Details

An attacker with permission to create Functions in their own namespace could set `spec.environment.namespace` to any other tenant's namespace. poolmgr and newdeploy would then look up and use the victim's Environment CRD when scheduling
function pods, so the attacker's function executed inside the victim's container image.

This is useful both for code and credential theft — the victim's runtime image may contain hardcoded secrets — and for confused-deputy attacks where the victim's runtime image is a privileged sidecar.

### Impact

A tenant with `functions.fission.io/create` could run their own function code inside another tenant's container image, breaking the namespace trust boundary that the Function specification implies.

### Fix

Fixed in [#3389](https://github.com/fission/fission/pull/3389) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0).

- **Admission webhook** (`pkg/webhook/function.go::Validate`) rejects `Function.spec.environment.namespace != metadata.namespace`. An empty namespace remains accepted (the CLI defaults it to the function's namespace).
- **Controller belt-and-braces:** the same check runs before the cross-namespace `Environments(...).Get` in poolmgr `getFunctionEnv` and newdeploy `fnCreate` / `RefreshFuncPods`, covering webhook-bypass clusters (`failurePolicy=Ignore`)
and stale Function objects from upgrade-before-restart windows.

### Behavioural change

Functions that explicitly set `spec.environment.namespace` to a different namespace are now rejected at admission. Empty-string remains accepted.

## References
- https://github.com/fission/fission/security/advisories/GHSA-cvw6-gfvv-953q
- https://nvd.nist.gov/vuln/detail/CVE-2026-49824
- https://github.com/fission/fission/pull/3389
- https://github.com/fission/fission/commit/80e7ba55228e1ef426f51353e25d2682ec61de34
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
