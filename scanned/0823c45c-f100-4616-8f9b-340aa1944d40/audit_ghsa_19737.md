# [M] Kubernetes allows Command Injection affecting Windows nodes via nodes/*/logs/query API

## Summary
Severity: Medium
Advisory: GHSA-vv39-3w5q-974q
CVE: CVE-2024-9042
CWE: CWE-20, CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-13
Source: https://github.com/advisories/GHSA-vv39-3w5q-974q
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.29.13
- Go: `k8s.io/kubernetes` — affected >=1.30.0-alpha.0 <1.30.9
- Go: `k8s.io/kubernetes` — affected >=1.31.0-alpha.0 <1.31.5
- Go: `k8s.io/kubernetes` — affected >=1.32.0-alpha.0 <1.32.1

## Details
A security vulnerability has been discovered in Kubernetes windows nodes that could allow a user with the ability to query a node's '/logs' endpoint to execute arbitrary commands on the host.  This CVE affects only Windows worker nodes. Your worker node is vulnerable to this issue if it is running one of the affected versions listed below.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-9042
- https://github.com/kubernetes/kubernetes/issues/129654
- https://github.com/kubernetes/kubernetes/commit/45f4ccc2153bbb782253704cbe24c05e22b5d60c
- https://github.com/kubernetes/kubernetes/commit/5fe148234f8ab1184f26069c4f7bef6c37efe347
- https://github.com/kubernetes/kubernetes/commit/75c83a6871dc030675288c6d63c275a43c2f0d55
- https://github.com/kubernetes/kubernetes/commit/fb0187c2bf7061258bb89891edb1237261eb7abc
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/9C3vn6aCSVg
- http://www.openwall.com/lists/oss-security/2025/01/16/1
