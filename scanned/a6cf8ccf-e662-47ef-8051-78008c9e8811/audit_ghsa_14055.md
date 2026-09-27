# [M] Ingress-nginx `path` sanitization can be bypassed with newline character

## Summary
Severity: Medium
Advisory: GHSA-863x-868h-968x
CVE: CVE-2021-25748
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-24
Source: https://github.com/advisories/GHSA-863x-868h-968x
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.2.1

## Details
A security issue was discovered in ingress-nginx where a user that can create or update ingress objects can use a newline character to bypass the sanitization of the `spec.rules[].http.paths[].path` field of an Ingress object (in the `networking.k8s.io` or `extensions` API group) to obtain the credentials of the ingress-nginx controller. In the default configuration, that credential has access to all secrets in the cluster.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25748
- https://github.com/kubernetes/ingress-nginx/issues/8686
- https://github.com/kubernetes/ingress-nginx/pull/8623
- https://github.com/kubernetes/ingress-nginx
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.2.1
- https://groups.google.com/g/kubernetes-security-announce/c/avaRYa9c7I8
