# [H] Kubernetes csi-proxy vulnerable to privilege escalation due to improper input validation

## Summary
Severity: High
Advisory: GHSA-r6cc-7wj7-gfx2
CVE: CVE-2023-3893
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-r6cc-7wj7-gfx2
Type: github-advisory

## Affected
- Go: `github.com/kubernetes-csi/csi-proxy/v2` — affected >=2.0.0-alpha.0 <2.0.0-alpha.1
- Go: `github.com/kubernetes-csi/csi-proxy` — affected >=0.1.0-rc1 <1.1.3
- Go: `github.com/kubernetes-csi/csi-proxy` — affected >=0 <0.0.0-20230821192013-2523e6674ded
- Go: `github.com/kubernetes-csi/csi-proxy` — affected >=1.1.3-0 <1.1.3-0.20230821192013-2523e6674ded

## Details
Kubernetes is vulnerable to privilege escalation when a user that can create pods on Windows nodes running kubernetes-csi-proxy may be able to escalate to admin privileges on those nodes. Kubernetes clusters are only affected if they include Windows nodes running kubernetes-csi-proxy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3893
- https://github.com/kubernetes/kubernetes/issues/119594
- https://github.com/kubernetes-csi/csi-proxy/commit/0e83a68159111e4ee510f5aa56d47ba97bda60c7
- https://github.com/kubernetes-csi/csi-proxy/commit/2523e6674dedf3de27f84235efec28555da24664
- https://github.com/kubernetes-csi/csi-proxy
- https://groups.google.com/g/kubernetes-security-announce/c/lWksE2BoCyQ
- https://security.netapp.com/advisory/ntap-20231221-0004
