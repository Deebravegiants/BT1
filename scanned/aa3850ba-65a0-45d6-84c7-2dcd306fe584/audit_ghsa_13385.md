# [M] kube-apiserver vulnerable to policy bypass

## Summary
Severity: Medium
Advisory: GHSA-qc2g-gmh6-95p4
CVE: CVE-2023-2727
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-03
Source: https://github.com/advisories/GHSA-qc2g-gmh6-95p4
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.27.0 <1.27.3
- Go: `k8s.io/kubernetes` — affected >=1.26.0 <1.26.6
- Go: `k8s.io/kubernetes` — affected >=1.25.0 <1.25.11
- Go: `k8s.io/kubernetes` — affected >=0 <1.24.15

## Details
Users may be able to launch containers using images that are restricted by ImagePolicyWebhook when using ephemeral containers. Kubernetes clusters are only affected if the ImagePolicyWebhook admission plugin is used together with ephemeral containers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2727
- https://github.com/kubernetes/kubernetes/issues/118640
- https://github.com/kubernetes/kubernetes/pull/118356
- https://github.com/kubernetes/kubernetes/pull/118471
- https://github.com/kubernetes/kubernetes/pull/118473
- https://github.com/kubernetes/kubernetes/pull/118474
- https://github.com/kubernetes/kubernetes/pull/118512
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/vPWYJ_L84m8
- https://security.netapp.com/advisory/ntap-20230803-0004
- http://www.openwall.com/lists/oss-security/2023/07/06/2
