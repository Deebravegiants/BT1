# [M] Privilege Escalation in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-33c5-9fx5-fvjm
CVE: CVE-2020-8559
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-33c5-9fx5-fvjm
Type: github-advisory

## Affected
- Go: `k8s.io/apimachinery` — affected >=0 <0.16.13
- Go: `k8s.io/apimachinery` — affected >=0.17.0 <0.17.9
- Go: `k8s.io/apimachinery` — affected >=0.18.0 <0.18.7
- Go: `k8s.io/kubernetes` — affected >=0 <1.16.13
- Go: `k8s.io/kubernetes` — affected >=1.17.0 <1.17.9
- Go: `k8s.io/kubernetes` — affected >=1.18.0 <1.18.7

## Details
The Kubernetes kube-apiserver in versions v1.6-v1.15, and versions prior to v1.16.13, v1.17.9 and v1.18.7 are vulnerable to an unvalidated redirect on proxied upgrade requests that could allow an attacker to escalate privileges from a node compromise to a full cluster compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8559
- https://github.com/kubernetes/kubernetes/issues/92914
- https://github.com/kubernetes/kubernetes/pull/92941
- https://bugzilla.redhat.com/show_bug.cgi?id=1851422
- https://github.com/kubernetes/kubernetes
- https://github.com/tdwyer/CVE-2020-8559
- https://groups.google.com/d/msg/kubernetes-security-announce/JAIGG5yNROs/19nHQ5wkBwAJ
- https://groups.google.com/g/kubernetes-security-announce/c/JAIGG5yNROs
- https://security.netapp.com/advisory/ntap-20200810-0004
