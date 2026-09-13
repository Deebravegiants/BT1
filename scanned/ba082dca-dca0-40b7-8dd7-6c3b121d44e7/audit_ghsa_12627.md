# [M] Kubelet vulnerable to bypass of seccomp profile enforcement

## Summary
Severity: Medium
Advisory: GHSA-xc8m-28vv-4pjc
CVE: CVE-2023-2431
CWE: CWE-1287
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-06-16
Source: https://github.com/advisories/GHSA-xc8m-28vv-4pjc
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.24.14
- Go: `k8s.io/kubernetes` — affected >=1.25.0 <1.25.10
- Go: `k8s.io/kubernetes` — affected >=1.26.0 <1.26.5
- Go: `k8s.io/kubernetes` — affected >=1.27.0 <1.27.2

## Details
A security issue was discovered in Kubelet that allows pods to bypass the seccomp profile enforcement. Pods that use localhost type for seccomp profile but specify an empty profile field, are affected by this issue. In this scenario, this vulnerability allows the pod to run in unconfined (seccomp disabled) mode. This bug affects Kubelet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2431
- https://github.com/kubernetes/kubernetes/issues/118690
- https://github.com/kubernetes/kubernetes/pull/117020
- https://github.com/kubernetes/kubernetes/pull/117116
- https://github.com/kubernetes/kubernetes/pull/117117
- https://github.com/kubernetes/kubernetes/pull/117118
- https://github.com/kubernetes/kubernetes/pull/117147
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/QHmx0HOQa10
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/43HDSKBKPSW53OW647B5ETHRWFFNHSRQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XBX4RL4UOC7JHWWYB2AJCKSUM7EG5Y5G
- https://pkg.go.dev/vuln/GO-2023-1864
