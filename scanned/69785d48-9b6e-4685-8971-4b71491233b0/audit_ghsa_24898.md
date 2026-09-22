# [H] Improper Input Validation in k8s.io/ingress-nginx

## Summary
Severity: High
Advisory: GHSA-pvmg-xgmx-9mxh
CVE: CVE-2021-25745
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-07
Source: https://github.com/advisories/GHSA-pvmg-xgmx-9mxh
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.2.0

## Details
A security issue was discovered in ingress-nginx where a user that can create or update ingress objects can use the spec.rules[].http.paths[].path field of an Ingress object (in the networking.k8s.io or extensions API group) to obtain the credentials of the ingress-nginx controller. In the default configuration, that credential has access to all secrets in the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25745
- https://github.com/kubernetes/ingress-nginx/issues/8502
- https://github.com/kubernetes/ingress-nginx
- https://groups.google.com/g/kubernetes-security-announce/c/7vQrpDZeBlc
- https://security.netapp.com/advisory/ntap-20220609-0006
