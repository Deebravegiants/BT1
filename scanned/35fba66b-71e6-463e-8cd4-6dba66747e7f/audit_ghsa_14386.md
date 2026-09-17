# [M] Kubernetes vulnerable to path traversal

## Summary
Severity: Medium
Advisory: GHSA-2394-5535-8j88
CVE: CVE-2022-3162
CWE: CWE-22, CWE-23
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-2394-5535-8j88
Type: github-advisory

## Affected
- Go: `github.com/kubernetes/kubernetes` — affected >=1.25.0 <1.25.4
- Go: `github.com/kubernetes/kubernetes` — affected >=1.24.0 <1.24.8
- Go: `github.com/kubernetes/kubernetes` — affected >=1.23.0 <1.23.14
- Go: `github.com/kubernetes/kubernetes` — affected >=1.22.0 <1.22.16

## Details
Users authorized to list or watch one type of namespaced custom resource cluster-wide can read custom resources of a different type in the same API group without authorization. Clusters are impacted by this vulnerability if all of the following are true: 1. There are 2+ CustomResourceDefinitions sharing the same API group 2. Users have cluster-wide list or watch authorization on one of those custom resources. 3. The same users are not authorized to read another custom resource in the same API group.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3162
- https://github.com/kubernetes/kubernetes/issues/113756
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/iUd550j7kjA
- https://security.netapp.com/advisory/ntap-20230511-0004
