# [M] Denial of service in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-55qj-gj3x-jq9r
CVE: CVE-2020-8557
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-55qj-gj3x-jq9r
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes/pkg/kubelet` — affected >=1.1.0 <1.16.13
- Go: `k8s.io/kubernetes/pkg/kubelet` — affected >=1.17.0 <1.17.9
- Go: `k8s.io/kubernetes/pkg/kubelet` — affected >=1.18.0 <1.18.6

## Details
The Kubernetes kubelet component in versions 1.1-1.16.12, 1.17.0-1.17.8 and 1.18.0-1.18.5 do not account for disk usage by a pod which writes to its own /etc/hosts file. The /etc/hosts file mounted in a pod by kubelet is not included by the kubelet eviction manager when calculating ephemeral storage usage by a pod. If a pod writes a large amount of data to the /etc/hosts file, it could fill the storage space of the node and cause the node to fail.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8557
- https://github.com/kubernetes/kubernetes/issues/93032
- https://github.com/kubernetes/kubernetes/pull/92921
- https://github.com/kubernetes/kubernetes/commit/530f199b6e07cdaab32361e39709ac45f3fdc446
- https://github.com/kubernetes/kubernetes/commit/68750fefd3df76b7b008ef7b18e8acd18d5c2f2e
- https://github.com/kubernetes/kubernetes/commit/7fd849cffa2f93061fbcb0a6ae4efd0539b1e981
- https://github.com/advisories/GHSA-55qj-gj3x-jq9r
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/cB_JUsYEKyY/m/vVSO61AhBwAJ
- https://pkg.go.dev/vuln/GO-2024-2753
- https://security.netapp.com/advisory/ntap-20200821-0002
