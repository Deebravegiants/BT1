# [M] Kube-proxy may unintentionally forward traffic

## Summary
Severity: Medium
Advisory: GHSA-35c7-w35f-xwgh
CVE: CVE-2021-25736
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-30
Source: https://github.com/advisories/GHSA-35c7-w35f-xwgh
Type: github-advisory

## Affected
- Go: `k8s.io/kubernetes` — affected >=0 <1.21.0

## Details
Kube-proxy on Windows can unintentionally forward traffic to local processes listening on the same port (`spec.ports[*].port`) as a LoadBalancer Service when the LoadBalancer controller does not set the `status.loadBalancer.ingress[].ip` field. Clusters 
where the LoadBalancer controller sets the `status.loadBalancer.ingress[].ip` field are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25736
- https://github.com/kubernetes/kubernetes/pull/99958
- https://github.com/kubernetes/kubernetes/commit/b014610de3e5cf1bb0f7844b5758d29fc18b75e6
- https://github.com/kubernetes/kubernetes
- https://groups.google.com/g/kubernetes-security-announce/c/lIoOPObO51Q/m/O15LOazPAgAJ
- https://security.netapp.com/advisory/ntap-20231221-0003
