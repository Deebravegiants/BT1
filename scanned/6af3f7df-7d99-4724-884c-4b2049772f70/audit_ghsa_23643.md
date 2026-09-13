# [M] ingress-nginx component for Kubernetes allows file overwrite

## Summary
Severity: Medium
Advisory: GHSA-hhpm-74pm-hf35
CVE: CVE-2020-8553
CWE: CWE-610, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hhpm-74pm-hf35
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <0.28.0

## Details
The Kubernetes ingress-nginx component prior to version 0.28.0 allows a user with the ability to create namespaces and to read and create ingress objects to overwrite the password file of another ingress which uses nginx.ingress.kubernetes.io/auth-type: basic and which has a hyphenated namespace or secret name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8553
- https://github.com/kubernetes/ingress-nginx/issues/5126
- https://github.com/kubernetes/ingress-nginx
