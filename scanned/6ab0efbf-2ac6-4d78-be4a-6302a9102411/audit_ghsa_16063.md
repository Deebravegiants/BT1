# [H]  Kubernetes kubelet arbitrary command execution

## Summary
Severity: High
Advisory: GHSA-27wf-5967-98gx
CVE: CVE-2024-10220
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-22
Source: https://github.com/advisories/GHSA-27wf-5967-98gx
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.28.12
- Go: `k8s.io/kubernetes` — affected >=1.29.0 <1.29.7
- Go: `k8s.io/kubernetes` — affected >=1.30.0 <1.30.3

## Details
The Kubernetes kubelet component allows arbitrary command execution via specially crafted gitRepo volumes.This issue affects kubelet: through 1.28.11, from 1.29.0 through 1.29.6, from 1.30.0 through 1.30.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10220
- https://github.com/kubernetes/kubernetes/issues/128885
- https://github.com/kubernetes/kubernetes/commit/1ab06efe92d8e898ca1931471c9533ce94aba29b
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/ptNgV5Necko
- https://pkg.go.dev/vuln/GO-2024-3286
- http://www.openwall.com/lists/oss-security/2024/11/20/1
