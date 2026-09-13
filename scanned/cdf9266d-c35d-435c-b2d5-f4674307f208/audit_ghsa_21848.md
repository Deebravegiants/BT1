# [M] Unverified Ownership in Kubernetes

## Summary
Severity: Medium
Advisory: GHSA-j9wf-vvm6-4r9w
CVE: CVE-2020-8554
CWE: CWE-283
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-08
Source: https://github.com/advisories/GHSA-j9wf-vvm6-4r9w
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0

## Details
Kubernetes API server in all versions allow an attacker who is able to create a ClusterIP service and set the spec.externalIPs field, to intercept traffic to that IP address. Additionally, an attacker who is able to patch the status (which is considered a privileged operation and should not typically be granted to users) of a LoadBalancer service can set the status.loadBalancer.ingress.ip to similar effect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8554
- https://github.com/kubernetes/kubernetes/issues/97076
- https://github.com/kubernetes/kubernetes/issues/97110
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://lists.apache.org/thread.html/rdb223e1b82e3d7d8e4eaddce8dd1ab87252e3935cc41c859f49767b6@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rdb223e1b82e3d7d8e4eaddce8dd1ab87252e3935cc41c859f49767b6%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rcafa485d63550657f068775801aeb706b7a07140a8ebbdef822b3bb3@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/rcafa485d63550657f068775801aeb706b7a07140a8ebbdef822b3bb3%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r1975078e44d96f2a199aa90aa874b57a202eaf7f25f2fde6d1c44942@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r1975078e44d96f2a199aa90aa874b57a202eaf7f25f2fde6d1c44942%40%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r0c76b3d0be348f788cd947054141de0229af00c540564711e828fd40@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r0c76b3d0be348f788cd947054141de0229af00c540564711e828fd40%40%3Ccommits.druid.apache.org%3E
- https://kubernetes.io/blog/2026/05/26/reconciling-unfixed-kubernetes-cves
- https://groups.google.com/g/kubernetes-security-announce/c/iZWsF9nbKE8
- https://github.com/kubernetes/kubernetes
