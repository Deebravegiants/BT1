# [H] Files or Directories Accessible to External Parties in kubernetes

## Summary
Severity: High
Advisory: GHSA-f5f7-6478-qm6p
CVE: CVE-2021-25741
CWE: CWE-20, CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-11-01
Source: https://github.com/advisories/GHSA-f5f7-6478-qm6p
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.19.15
- Go: `k8s.io/kubernetes` — affected >=1.20.0 <1.20.11
- Go: `k8s.io/kubernetes` — affected >=1.21.0 <1.21.5
- Go: `k8s.io/kubernetes` — affected >=1.22.0 <1.22.2

## Details
A security issue was discovered in Kubernetes where a user may be able to create a container with subpath volume mounts to access files & directories outside of the volume, including on the host filesystem.

## References
- https://github.com/bottlerocket-os/bottlerocket/security/advisories/GHSA-f5f7-6478-qm6p
- https://nvd.nist.gov/vuln/detail/CVE-2021-25741
- https://github.com/kubernetes/kubernetes/issues/104980
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/nyfdhK24H7s
- https://security.netapp.com/advisory/ntap-20211008-0006
