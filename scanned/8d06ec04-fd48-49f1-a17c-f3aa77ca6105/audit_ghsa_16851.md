# [M] Kubelet Incorrect Privilege Assignment

## Summary
Severity: Medium
Advisory: GHSA-r76g-g87f-vw8f
CVE: CVE-2019-11245
CWE: CWE-266, CWE-703
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-r76g-g87f-vw8f
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes/cmd/kubelet` — affected >=1.14.0 <1.14.3
- Go: `k8s.io/kubernetes/cmd/kubelet` — affected >=1.13.0 <1.13.7

## Details
In kubelet v1.13.6 and v1.14.2, containers for pods that do not specify an explicit `runAsUser` attempt to run as uid 0 (root) on container restart, or if the image was previously pulled to the node. If the pod specified `mustRunAsNonRoot: true`, the kubelet will refuse to start the container as root. If the pod did not specify `mustRunAsNonRoot: true`, the kubelet will run the container as uid 0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11245
- https://github.com/kubernetes/kubernetes/issues/78308
- https://github.com/kubernetes/kubernetes/pull/76665
- https://github.com/kubernetes/kubernetes/pull/76665/commits/26e3c8674e66f0d10170d34f5445f0aed207387f
- https://bugzilla.redhat.com/show_bug.cgi?id=1715726
- https://github.com/advisories/GHSA-r76g-g87f-vw8f
- https://github.com/kubernetes/kubernetes
- https://pkg.go.dev/vuln/GO-2024-2780
- https://security.netapp.com/advisory/ntap-20190919-0003
