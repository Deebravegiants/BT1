# [H] Kubernetes vulnerable to validation bypass

## Summary
Severity: High
Advisory: GHSA-jh36-q97c-9928
CVE: CVE-2022-3294
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-jh36-q97c-9928
Type: github-advisory

## Affected
- Go: `github.com/kubernetes/kubernetes` — affected >=1.25.0 <1.25.4
- Go: `github.com/kubernetes/kubernetes` — affected >=1.24.0 <1.24.8
- Go: `github.com/kubernetes/kubernetes` — affected >=1.23.0 <1.23.14
- Go: `github.com/kubernetes/kubernetes` — affected >=1.22.0 <1.22.16

## Details
Users may have access to secure endpoints in the control plane network. Kubernetes clusters are only affected if an untrusted user can modify Node objects and send proxy requests to them. Kubernetes supports node proxying, which allows clients of kube-apiserver to access endpoints of a Kubelet to establish connections to Pods, retrieve container logs, and more. While Kubernetes already validates the proxying address for Nodes, a bug in kube-apiserver made it possible to bypass this validation. Bypassing this validation could allow authenticated requests destined for Nodes to to the API server's private network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3294
- https://github.com/kubernetes/kubernetes/issues/113757
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/VyPOxF7CIbA
- https://security.netapp.com/advisory/ntap-20230505-0007
