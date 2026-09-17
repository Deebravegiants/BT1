# [M] Kubernetes GitRepo Volume Inadvertent Local Repository Access

## Summary
Severity: Medium
Advisory: GHSA-3wgm-2gw2-vh5m
CVE: CVE-2025-1767
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-13
Source: https://github.com/advisories/GHSA-3wgm-2gw2-vh5m
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0

## Details
A security vulnerability was discovered in Kubernetes that could allow a user with create pod permission to exploit gitRepo volumes to access local git repositories belonging to other pods on the same node. This CVE only affects Kubernetes clusters that utilize the in-tree gitRepo volume to clone git repositories from other pods within the same node. Since the in-tree gitRepo volume feature has been deprecated and will not receive security updates upstream, any cluster still using this feature remains vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1767
- https://github.com/kubernetes/kubernetes/pull/130786
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/19irihsKg7s
- http://www.openwall.com/lists/oss-security/2025/03/13/9
