# [M] Kubernetes client-go library logs may disclose credentials to unauthorized users

## Summary
Severity: Medium
Advisory: GHSA-jmrx-5g74-6v2f
CVE: CVE-2019-11250
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jmrx-5g74-6v2f
Type: github-advisory

## Affected
- Go: `k8s.io/client-go` — affected >=0 <0.17.0
- Go: `k8s.io/kubernetes` — affected >=0 <1.16.0-beta.1

## Details
The Kubernetes client-go library logs request headers at verbosity levels of 7 or higher. This can disclose credentials to unauthorized users via logs or command output. Kubernetes components (such as kube-apiserver) prior to v1.16.0, which make use of basic or bearer token authentication, and run at high verbosity levels, are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11250
- https://github.com/kubernetes/kubernetes/issues/81114
- https://github.com/kubernetes/kubernetes/pull/81330
- https://github.com/kubernetes/kubernetes/commit/4441f1d9c3e94d9a3d93b4f184a591cab02a5245
- https://access.redhat.com/errata/RHSA-2019:4052
- https://access.redhat.com/errata/RHSA-2019:4087
- https://github.com/kubernetes/kubernetes
- https://pkg.go.dev/vuln/GO-2021-0065
- https://security.netapp.com/advisory/ntap-20190919-0003
- http://www.openwall.com/lists/oss-security/2020/10/16/2
