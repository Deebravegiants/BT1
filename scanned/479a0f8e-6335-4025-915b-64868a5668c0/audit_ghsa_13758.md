# [H] Kubernetes Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-hq6q-c2x6-hmch
CVE: CVE-2023-5528
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-hq6q-c2x6-hmch
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.28.0 <1.28.4
- Go: `k8s.io/kubernetes` — affected >=1.27.0 <1.27.8
- Go: `k8s.io/kubernetes` — affected >=1.26.0 <1.26.11
- Go: `k8s.io/kubernetes` — affected >=0 <1.25.16

## Details
A security issue was discovered in Kubernetes where a user that can create pods and persistent volumes on Windows nodes may be able to escalate to admin privileges on those nodes. Kubernetes clusters are only affected if they are using an in-tree storage plugin for Windows nodes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5528
- https://github.com/kubernetes/kubernetes/issues/121879
- https://github.com/kubernetes/kubernetes/pull/121881
- https://github.com/kubernetes/kubernetes/pull/121882
- https://github.com/kubernetes/kubernetes/pull/121883
- https://github.com/kubernetes/kubernetes/pull/121884
- https://github.com/kubernetes/kubernetes/pull/121885
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/SL_d4NR8pzA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3JH444PWZBINXLLFV7XLIJIZJHSK6UEZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4XZIX727JIKF5RQW7RVVBLWXBCDIBJA7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7MPGMITSZXUCAVO7Q75675SOLXC2XXU4
- https://security.netapp.com/advisory/ntap-20240119-0009
