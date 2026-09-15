# [M] Kubernetes mountable secrets policy bypass

## Summary
Severity: Medium
Advisory: GHSA-cgcv-5272-97pr
CVE: CVE-2023-2728
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-07-03
Source: https://github.com/advisories/GHSA-cgcv-5272-97pr
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.27.0 <1.27.3
- Go: `k8s.io/kubernetes` — affected >=1.26.0 <1.26.6
- Go: `k8s.io/kubernetes` — affected >=1.25.0 <1.25.11
- Go: `k8s.io/kubernetes` — affected >=0 <1.24.15

## Details
Users may be able to launch containers that bypass the mountable secrets policy enforced by the ServiceAccount admission plugin when using ephemeral containers. The policy ensures pods running with a service account may only reference secrets specified in the service account’s secrets field. Kubernetes clusters are only affected if the ServiceAccount admission plugin and the `kubernetes.io/enforce-mountable-secrets` annotation are used together with ephemeral containers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2728
- https://github.com/kubernetes/kubernetes/issues/118640
- https://github.com/kubernetes/kubernetes/pull/118356
- https://github.com/kubernetes/kubernetes/pull/118471
- https://github.com/kubernetes/kubernetes/pull/118473
- https://github.com/kubernetes/kubernetes/pull/118474
- https://github.com/kubernetes/kubernetes/pull/118512
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/vPWYJ_L84m8
- https://security.netapp.com/advisory/ntap-20230803-0004
- http://www.openwall.com/lists/oss-security/2023/07/06/3
