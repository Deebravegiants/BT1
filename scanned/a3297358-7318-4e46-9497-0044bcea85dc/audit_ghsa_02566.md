# [M] Incomplete List of Disallowed Inputs in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-mfv7-gq43-w965
CVE: CVE-2021-25737
CWE: CWE-184, CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-mfv7-gq43-w965
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.16.0 <1.18.19
- Go: `k8s.io/kubernetes` — affected >=1.19.0 <1.19.11
- Go: `k8s.io/kubernetes` — affected >=1.20.0 <1.20.7
- Go: `k8s.io/kubernetes` — affected >=1.21.0 <1.21.1

## Details
A security issue was discovered in Kubernetes where a user may be able to redirect pod traffic to private networks on a Node. Kubernetes already prevents creation of Endpoint IPs in the localhost or link-local range, but the same validation was not performed on EndpointSlice IPs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25737
- https://github.com/kubernetes/kubernetes/issues/102106
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/xAiN3924thY
- https://security.netapp.com/advisory/ntap-20211004-0004
