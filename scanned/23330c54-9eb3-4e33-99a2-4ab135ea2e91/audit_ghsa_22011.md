# [M] Allocation of Resources Without Limits or Throttling and Uncontrolled Memory Allocation in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-qhm4-jxv7-j9pq
CVE: CVE-2020-8551
CWE: CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-qhm4-jxv7-j9pq
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.15.0 <1.15.10
- Go: `k8s.io/kubernetes` — affected >=1.16.0 <1.16.6
- Go: `k8s.io/kubernetes` — affected >=1.17.0 <1.17.2

## Details
The Kubelet component in versions 1.15.0-1.15.9, 1.16.0-1.16.6, and 1.17.0-1.17.2 has been found to be vulnerable to a denial of service attack via the kubelet API, including the unauthenticated HTTP read-only API typically served on port 10255, and the authenticated HTTPS API typically served on port 10250.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8551
- https://github.com/kubernetes/kubernetes/issues/89377
- https://github.com/kubernetes/kubernetes/pull/87913
- https://github.com/kubernetes/kubernetes/commit/9802bfcec0580169cffce2a3d468689a407fa7dc
- https://groups.google.com/forum/#!topic/kubernetes-security-announce/2UOlsba2g0s
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3SOCLOPTSYABTE4CLTSPDIFE6ZZZR4LX
- https://security.netapp.com/advisory/ntap-20200413-0003
