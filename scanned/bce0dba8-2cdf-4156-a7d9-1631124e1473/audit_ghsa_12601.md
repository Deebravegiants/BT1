# [M] Kyverno resource with a deletionTimestamp may allow policy circumvention

## Summary
Severity: Medium
Advisory: GHSA-hq4m-4948-64cc
CVE: CVE-2023-34091
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-05
Source: https://github.com/advisories/GHSA-hq4m-4948-64cc
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=0 <1.10.0

## Details
### Impact

In versions of Kyverno prior to 1.10.0, resources which have the `deletionTimestamp` field defined can bypass validate, generate, or mutate-existing policies, even in cases where the `validationFailureAction` field is set to `Enforce`. 

This situation occurs as resources pending deletion were being consciously exempted by Kyverno, as a way to reduce processing load as policies are typically not applied to objects which are being deleted. 

However, this could potentially result in allowing a malicious user to leverage the [Kubernetes finalizers feature](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/) by setting a finalizer which causes the Kubernetes API server to set the `deletionTimestamp` and then not completing the delete operation as a way to explicitly to bypass a Kyverno policy. 

Note that this is not applicable to Kubernetes Pods but, as an example, a Kubernetes Service resource can be manipulated using an indefinite finalizer to bypass policies.


### Patches
This is resolved in Kyverno 1.10.0.

### Workarounds
There is no known workaround.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-hq4m-4948-64cc
- https://nvd.nist.gov/vuln/detail/CVE-2023-34091
- https://github.com/kyverno/kyverno
- https://github.com/kyverno/kyverno/releases/tag/v1.10.0
