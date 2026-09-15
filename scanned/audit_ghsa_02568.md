# [M] Confused Deputy in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-74j8-88mm-7496
CVE: CVE-2020-8561
CWE: CWE-441, CWE-610
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2021-09-21
Source: https://github.com/advisories/GHSA-74j8-88mm-7496
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0

## Details
A security issue was discovered in Kubernetes where actors that control the responses of MutatingWebhookConfiguration or ValidatingWebhookConfiguration requests are able to redirect kube-apiserver requests to private networks of the apiserver. If that user can view kube-apiserver logs when the log level is set to 10, they can view the redirected responses and headers in the logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8561
- https://github.com/kubernetes/kubernetes/issues/104720
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/RV2IhwcrQsY
- https://kubernetes.io/blog/2026/05/26/reconciling-unfixed-kubernetes-cves
- https://security.netapp.com/advisory/ntap-20211014-0002
