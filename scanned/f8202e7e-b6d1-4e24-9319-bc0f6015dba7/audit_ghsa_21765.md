# [M] Kubernetes API Server DoS Via API Requests

## Summary
Severity: Medium
Advisory: GHSA-82hx-w2r5-c2wq
CVE: CVE-2020-8552
CWE: CWE-400, CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-82hx-w2r5-c2wq
Type: github-advisory

## Affected
- Go: `k8s.io/apiserver` — affected >=0 <0.15.10
- Go: `k8s.io/apiserver` — affected >=0.16.0 <0.16.7
- Go: `k8s.io/apiserver` — affected >=0.17.0 <0.17.3

## Details
The Kubernetes API server component in Kubernetes versions prior to 1.15.9, 1.16.0-1.16.6, and 1.17.0-1.17.2 has been found to be vulnerable to a denial of service attack via successful API requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8552
- https://github.com/kubernetes/kubernetes/issues/89378
- https://github.com/kubernetes/kubernetes/pull/87669
- https://github.com/kubernetes/kubernetes/commit/5978856c4c7f10737a11c9540fe60b8475beecbb
- https://groups.google.com/forum/#!topic/kubernetes-security-announce/2UOlsba2g0s
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3SOCLOPTSYABTE4CLTSPDIFE6ZZZR4LX
- https://security.netapp.com/advisory/ntap-20200413-0003
