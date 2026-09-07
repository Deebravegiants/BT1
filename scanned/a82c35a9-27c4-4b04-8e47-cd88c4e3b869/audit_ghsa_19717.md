# [M] ingress-nginx controller - auth secret file path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-242m-6h72-7hgp
CVE: CVE-2025-24513
CWE: CWE-20, CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-242m-6h72-7hgp
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.11.5
- Go: `k8s.io/ingress-nginx` — affected >=1.12.0-beta.0 <1.12.1

## Details
A security issue was discovered in [ingress-nginx](https://github.com/kubernetes/ingress-nginx) where attacker-provided data are included in a filename by the ingress-nginx Admission Controller feature, resulting in directory traversal within the container. This could result in denial of service, or when combined with other vulnerabilities, limited disclosure of Secret objects from the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-24513
- https://github.com/kubernetes/kubernetes/issues/131005
- https://github.com/kubernetes/ingress-nginx
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.11.5
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.12.1
- https://groups.google.com/g/kubernetes-security-announce/c/2qa9DFtN0cQ
- https://security.netapp.com/advisory/ntap-20250328-0008
