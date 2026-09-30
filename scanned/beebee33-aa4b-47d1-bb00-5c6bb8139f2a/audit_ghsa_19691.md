# [C] ingress-nginx admission controller RCE escalation

## Summary
Severity: Critical
Advisory: GHSA-mgvx-rpfc-9mpv
CVE: CVE-2025-1974
CWE: CWE-653
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-25
Source: https://github.com/advisories/GHSA-mgvx-rpfc-9mpv
Type: github-advisory

## Affected
- Go: `k8s.io/ingress-nginx` — affected >=0 <1.11.5
- Go: `k8s.io/ingress-nginx` — affected >=1.12.0-beta.0 <1.12.1

## Details
A security issue was discovered in Kubernetes where under certain conditions, an unauthenticated attacker with access to the pod network can achieve arbitrary code execution in the context of the ingress-nginx controller. This can lead to disclosure of Secrets accessible to the controller. (Note that in the default installation, the controller can access all Secrets cluster-wide.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1974
- https://github.com/kubernetes/kubernetes/issues/131009
- https://github.com/B1ack4sh/Blackash-CVE-2025-1974
- https://github.com/kubernetes/ingress-nginx
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.11.5
- https://github.com/kubernetes/ingress-nginx/releases/tag/controller-v1.12.1
- https://groups.google.com/g/kubernetes-security-announce/c/2qa9DFtN0cQ
- https://https://github.com/kubernetes/kubernetes/issues/131009
- https://security.netapp.com/advisory/ntap-20250328-0008
- https://www.exploit-db.com/exploits/52475
