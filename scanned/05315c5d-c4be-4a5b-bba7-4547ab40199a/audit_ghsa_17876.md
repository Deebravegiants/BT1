# [M] Kubernetes Nodes can delete themselves by adding an OwnerReference

## Summary
Severity: Medium
Advisory: GHSA-4x4m-3c2p-qppc
CVE: CVE-2025-5187
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-08-27
Source: https://github.com/advisories/GHSA-4x4m-3c2p-qppc
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.31.12
- Go: `k8s.io/kubernetes` — affected >=1.32.0-alpha.0 <1.32.8
- Go: `k8s.io/kubernetes` — affected >=1.33.0-alpha.0 <1.33.4

## Details
A vulnerability exists in the NodeRestriction admission controller in Kubernetes clusters where node users can delete their corresponding node object by patching themselves with an OwnerReference to a cluster-scoped resource. If the OwnerReference resource does not exist or is subsequently deleted, the given node object will be deleted via garbage collection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5187
- https://github.com/kubernetes/kubernetes/issues/133471
- https://github.com/kubernetes/kubernetes/commit/a2d98cac56a0c5cb2d8abc4d087fc00846b3bc0f
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/znSNY7XCztE
