# [M] Kubernetes Unsafe Cacheing 

## Summary
Severity: Medium
Advisory: GHSA-2575-pghm-6qqx
CVE: CVE-2019-11244
CWE: CWE-524, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-2575-pghm-6qqx
Type: github-advisory

## Affected
- Go: `k8s.io/client-go` — affected >=1.8.0 <1.12.9

## Details
In Kubernetes v1.8.x-v1.14.x, schema info is cached by kubectl in the location specified by `--cache-dir` (defaulting to `$HOME/.kube/http-cache`), written with world-writeable permissions (`rw-rw-rw-`). If `--cache-dir` is specified and pointed at a different location accessible to other users/groups, the written files may be modified by other users/groups and disrupt the kubectl invocation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11244
- https://github.com/kubernetes/kubernetes/issues/76676
- https://github.com/kubernetes/kubernetes/pull/77874
- https://github.com/kubernetes/kubernetes/pull/77874/commits/f228ae3364729caed59087e23c42868454bc3ff4
- https://github.com/kubernetes/client-go/commit/790a4f63632139cf6731014d00a9a8338f1fbd7d
- https://access.redhat.com/errata/RHSA-2019:3942
- https://access.redhat.com/errata/RHSA-2020:0020
- https://access.redhat.com/errata/RHSA-2020:0074
- https://security.netapp.com/advisory/ntap-20190509-0002
- http://www.securityfocus.com/bid/108064
