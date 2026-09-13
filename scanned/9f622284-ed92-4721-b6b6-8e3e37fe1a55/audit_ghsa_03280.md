# [C] Kubernetes Privilege Escalation

## Summary
Severity: Critical
Advisory: GHSA-2jx2-76rc-2v7v
CVE: CVE-2017-1000056
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-12
Source: https://github.com/advisories/GHSA-2jx2-76rc-2v7v
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.5.0 <1.5.5

## Details
Kubernetes version 1.5.0-1.5.4 is vulnerable to a privilege escalation in the PodSecurityPolicy admission plugin resulting in the ability to make use of any existing PodSecurityPolicy object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000056
- https://github.com/kubernetes/kubernetes/issues/43459
- https://github.com/kubernetes/kubernetes/commit/7fef0a4f6a44ea36f166c39fdade5324eff2dd5e
- https://github.com/kubernetes/kubernetes
