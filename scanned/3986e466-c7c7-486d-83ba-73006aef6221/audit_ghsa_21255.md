# [M] Improper use of metav1.Duration allows for Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-f4p5-x4vc-mh4v
CVE: CVE-2022-39272
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-f4p5-x4vc-mh4v
Type: github-advisory

## Affected
- Go: `github.com/fluxcd/flux2` — affected >=0.1.0 <0.35.0
- Go: `github.com/fluxcd/source-controller` — affected >=0.0.1-alpha-1 <0.30.0
- Go: `github.com/fluxcd/kustomize-controller` — affected >=0.0.1-alpha-1 <0.29.0
- Go: `github.com/fluxcd/helm-controller` — affected >=0.0.1-alpha-1 <0.24.0
- Go: `github.com/fluxcd/notification-controller` — affected >=0.0.1-alpha-1 <0.27.0
- Go: `github.com/fluxcd/image-automation-controller` — affected >=0.1.0 <0.26.0
- Go: `github.com/fluxcd/image-reflector-controller` — affected >=0.1.0 <0.22.0
- Go: `github.com/fluxcd/helm-controller/api` — affected >=0 <0.26.0
- Go: `github.com/fluxcd/image-automation-controller/api` — affected >=0 <0.26.1
- Go: `github.com/fluxcd/image-reflector-controller/api` — affected >=0 <0.22.1
- Go: `github.com/fluxcd/kustomize-controller/api` — affected >=0 <0.30.0
- Go: `github.com/fluxcd/notification-controller/api` — affected >=0 <0.28.0
- Go: `github.com/fluxcd/source-controller/api` — affected >=0 <0.30.0

## Details
Flux controllers within the affected versions range are vulnerable to a denial of service attack. Users that have permissions to change Flux’s objects, either through a Flux source or directly within a cluster, can provide invalid data to fields `.spec.interval` or `.spec.timeout` (and structured variations of these fields), causing the entire object type to stop being processed.

The issue has two root causes: a) the Kubernetes type `metav1.Duration` not being fully compatible with the Go type `time.Duration` as explained on [upstream report](https://github.com/kubernetes/apimachinery/issues/131); b) lack of validation within Flux to restrict allowed values.

### Workarounds

Admission controllers can be employed to restrict the values that can be used for fields `.spec.interval` and `.spec.timeout`, however upgrading to the latest versions is still the recommended mitigation.

### Credits

This issue was reported by Alexander Block (@codablock) through the Flux security mailing list (as [recommended](https://fluxcd.io/security/#report-a-vulnerability)).

### For more information

If you have any questions or comments about this advisory:

- Open an issue in any of the affected repositories.
- Contact us at the CNCF Flux channel.

### References

- https://github.com/kubernetes/apimachinery/issues/131

## References
- https://github.com/fluxcd/flux2/security/advisories/GHSA-f4p5-x4vc-mh4v
- https://nvd.nist.gov/vuln/detail/CVE-2022-39272
- https://github.com/kubernetes/apimachinery/issues/131
- https://github.com/fluxcd/helm-controller/pull/533
- https://github.com/fluxcd/image-automation-controller/pull/439
- https://github.com/fluxcd/image-reflector-controller/pull/314
- https://github.com/fluxcd/kustomize-controller/pull/731
- https://github.com/fluxcd/notification-controller/pull/420
- https://github.com/fluxcd/source-controller/pull/903
- https://github.com/fluxcd/flux2
- https://github.com/kubernetes/apimachinery#131
- https://pkg.go.dev/vuln/GO-2022-1071
