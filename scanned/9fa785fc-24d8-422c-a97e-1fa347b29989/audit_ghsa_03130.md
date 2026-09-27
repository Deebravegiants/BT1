# [H] XML Entity Expansion and Improper Input Validation in Kubernetes API server

## Summary
Severity: High
Advisory: GHSA-pmqp-h87c-mr78
CVE: CVE-2019-11253
CWE: CWE-20, CWE-776
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-pmqp-h87c-mr78
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.0.0 <1.13.12
- Go: `k8s.io/kubernetes` — affected >=1.14.0 <1.14.8
- Go: `k8s.io/kubernetes` — affected >=1.15.0 <1.15.5
- Go: `k8s.io/kubernetes` — affected >=1.16.0 <1.16.2

## Details
Improper input validation in the Kubernetes API server in versions v1.0-1.12 and versions prior to v1.13.12, v1.14.8, v1.15.5, and v1.16.2 allows authorized users to send malicious YAML or JSON payloads, causing the API server to consume excessive CPU or memory, potentially crashing and becoming unavailable. Prior to v1.14.0, default RBAC policy authorized anonymous users to submit requests that could trigger this vulnerability. Clusters upgraded from a version prior to v1.14.0 keep the more permissive policy by default for backwards compatibility.

### Specific Go Packages Affected
k8s.io/kubernetes/pkg/apiserver

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11253
- https://github.com/kubernetes/kubernetes/issues/83253
- https://github.com/kubernetes/kubernetes/pull/83261
- https://access.redhat.com/errata/RHSA-2019:3239
- https://access.redhat.com/errata/RHSA-2019:3811
- https://access.redhat.com/errata/RHSA-2019:3905
- https://gist.github.com/bgeesaman/0e0349e94cd22c48bf14d8a9b7d6b8f2
- https://groups.google.com/forum/#!topic/kubernetes-security-announce/jk8polzSUxs
- https://pkg.go.dev/vuln/GO-2022-0703
- https://security.netapp.com/advisory/ntap-20191031-0006
