# [H] Minikube RCE via DNS Rebinding

## Summary
Severity: High
Advisory: GHSA-6pcv-qqx4-mxm3
CVE: CVE-2018-1002103
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6pcv-qqx4-mxm3
Type: github-advisory

## Affected
- Go: `k8s.io/minikube` — affected >=0.3.0

## Details
In Minikube versions 0.3.0-0.29.0, minikube exposes the Kubernetes Dashboard listening on the VM IP at port 30000. In VM environments where the IP is easy to predict, the attacker can use DNS rebinding to indirectly make requests to the Kubernetes Dashboard, create a new Kubernetes Deployment running arbitrary code. If minikube mount is in use, the attacker could also directly access the host filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002103
- https://github.com/kubernetes/minikube/issues/3208
