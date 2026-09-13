# [M] Node Denial of Service via kubelet Checkpoint API

## Summary
Severity: Medium
Advisory: GHSA-jgfp-53c3-624w
CVE: CVE-2025-0426
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-13
Source: https://github.com/advisories/GHSA-jgfp-53c3-624w
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.32.0 <1.32.2
- Go: `k8s.io/kubernetes` — affected >=1.31.0 <1.31.6
- Go: `k8s.io/kubernetes` — affected >=1.30.0 <1.30.10
- Go: `k8s.io/kubernetes` — affected >=0 <1.29.14

## Details
A security issue was discovered in Kubernetes where a large number of container checkpoint requests made to the unauthenticated kubelet read-only HTTP endpoint may cause a Node Denial of Service by filling the Node's disk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0426
- https://github.com/kubernetes/kubernetes/issues/130016
- https://github.com/advisories/GHSA-jgfp-53c3-624w
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/KiODfu8i6w8
- http://www.openwall.com/lists/oss-security/2025/02/13/1
