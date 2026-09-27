# [H] ingress-nginx controller - configuration injection via unsanitized mirror annotations

## Summary
Severity: High
Advisory: GHSA-vg63-w3p9-jc9m
CVE: CVE-2025-1098
CWE: CWE-15, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-vg63-w3p9-jc9m
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.11.5
- Go: `k8s.io/ingress-nginx` — affected >=1.12.0-beta.0 <1.12.1

## Details
A security issue was discovered in [ingress-nginx](https://github.com/kubernetes/ingress-nginx) where the `mirror-target` and `mirror-host` Ingress annotations can be used to inject arbitrary configuration into nginx. This can lead to arbitrary code execution in the context of the ingress-nginx controller, and disclosure of Secrets accessible to the controller. (Note that in the default installation, the controller can access all Secrets cluster-wide.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1098
- https://github.com/kubernetes/kubernetes/issues/131008
- https://github.com/kubernetes/ingress-nginx
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.11.5
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.12.1
- https://groups.google.com/g/kubernetes-security-announce/c/2qa9DFtN0cQ
- https://security.netapp.com/advisory/ntap-20250328-0008
