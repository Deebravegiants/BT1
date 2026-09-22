# [H] Fission: Cross-namespace Package read via unvalidated PackageRef in Function admission webhook

## Summary
Severity: High
Advisory: GHSA-3r8v-2xmj-5c39
CVE: CVE-2026-49823
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-3r8v-2xmj-5c39
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

A Fission Function spec carries three reference types — Secret, ConfigMap, and Package. The first two were namespace-validated by the admission webhook; `PackageRef.Namespace` was not.

### Details

A tenant with `functions.fission.io/create` in their own namespace could set `spec.package.packageref.namespace` to any other namespace. When the function is invoked, the fetcher sidecar reads the victim Package using the
`fission-fetcher` service account's namespace-wide `get packages` permission and writes its contents to `/userfunc/deployarchive` inside the attacker's pool pod, exposing the victim's source code and any embedded credentials.

The `fission-fetcher` SA holds `get packages` in every configured function namespace (granted by `charts/fission-all/templates/_function-access-role.tpl`), so the namespace check was the only barrier between the attacker and any
in-cluster Fission Package.

### Impact

A function author in one namespace could read the deployment archive — and therefore the source code and embedded secrets — of any Package in any other namespace.

### Fix

Fixed in [#3389](https://github.com/fission/fission/pull/3389) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0).

The admission webhook (`pkg/webhook/function.go::Validate`) rejects `Function.spec.package.packageref.namespace != metadata.namespace`. An empty namespace remains accepted (controllers default it to the function's namespace). This
shipped together with the EnvironmentRef cross-namespace check (GHSA-cvw6-gfvv-953q).

### Behavioural change

Functions that explicitly set `spec.package.packageref.namespace` to a different namespace are now rejected at admission.

## References
- https://github.com/fission/fission/security/advisories/GHSA-3r8v-2xmj-5c39
- https://nvd.nist.gov/vuln/detail/CVE-2026-49823
- https://github.com/fission/fission/pull/3389
- https://github.com/fission/fission/commit/80e7ba55228e1ef426f51353e25d2682ec61de34
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
