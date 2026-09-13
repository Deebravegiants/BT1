# [M] Directory Traversal in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-jp32-vmm6-3vf5
CVE: CVE-2015-5305
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-jp32-vmm6-3vf5
Type: github-advisory

## Affected
- Go: `github.com/kubernetes/kubernetes` — affected >=0 <1.1.1
- Go: `k8s.io/kubernetes` — affected >=0 <1.1.1

## Details
Directory traversal vulnerability in Kubernetes, as used in Red Hat OpenShift Enterprise 3.0, allows attackers to write to arbitrary files via a crafted object type name, which is not properly handled before passing it to etcd.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5305
- https://github.com/kubernetes/kubernetes/pull/16381
- https://github.com/kubernetes/kubernetes/commit/37f730f68c7f06e060f90714439bfb0dbb2df5e7
- https://github.com/kubernetes/kubernetes/commit/68f2add9bd5d43b9da1424d87d88f83d120e17d0
- https://access.redhat.com/errata/RHSA-2015:1945
- https://access.redhat.com/security/cve/CVE-2015-5305
- https://bugzilla.redhat.com/show_bug.cgi?id=1273969
- https://github.com/kubernetes/kubernetes
- https://pkg.go.dev/vuln/GO-2022-0701
- https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2015-5305
