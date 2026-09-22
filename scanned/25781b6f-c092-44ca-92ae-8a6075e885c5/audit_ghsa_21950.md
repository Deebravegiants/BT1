# [H] Improper Authentication in Kubernetes

## Summary
Severity: High
Advisory: GHSA-wqv3-8cm6-h6wg
CVE: CVE-2020-8558
CWE: CWE-420
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-wqv3-8cm6-h6wg
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=1.18.0 <1.18.4
- Go: `k8s.io/kubernetes` — affected >=1.17.0 <1.17.7
- Go: `k8s.io/kubernetes` — affected >=0 <1.16.11

## Details
A security issue was discovered in the Kubelet and kube-proxy components of Kubernetes which allows adjacent hosts to reach TCP and UDP services bound to 127.0.0.1 running on the node or in the node's network namespace. For example, if a cluster administrator runs a TCP service on a node that listens on 127.0.0.1:1234, because of this bug, that service would be potentially reachable by other hosts on the same LAN as the node, or by containers running on the same node as the service. If the example service on port 1234 required no additional authentication (because it assumed that only other localhost processes could reach it), then it could be vulnerable to attacks that make use of this bug.

## References
- https://github.com/bottlerocket-os/bottlerocket/security/advisories/GHSA-wqv3-8cm6-h6wg
- https://nvd.nist.gov/vuln/detail/CVE-2020-8558
- https://github.com/kubernetes/kubernetes/issues/92315
- https://bugzilla.redhat.com/show_bug.cgi?id=1843358
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-8558
- https://github.com/kubernetes/kubernetes
- https://github.com/tabbysable/POC-2020-8558
- https://groups.google.com/g/kubernetes-announce/c/sI4KmlH3S2I/m/TljjxOBvBQAJ
- https://groups.google.com/g/kubernetes-security-announce/c/B1VegbBDMTE
- https://labs.bishopfox.com/tech-blog/bad-pods-kubernetes-pod-privilege-escalation
- https://security.netapp.com/advisory/ntap-20200821-0001
- https://www.openwall.com/lists/oss-security/2020/07/08/1
