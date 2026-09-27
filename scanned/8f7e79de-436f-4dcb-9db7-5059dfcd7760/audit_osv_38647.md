# [M] ServiceAccount token disclosure via install-cni container logs

## Summary
Severity: Medium
Advisory: CVE-2026-41184
Aliases: GHSA-9p7w-w5q6-mxj3, GO-2026-5888
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:L)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-41184
Type: osv

## Details
In Calico, the install-cni init container logs the rendered CNI configuration to standard output. When the configuration template uses the __SERVICEACCOUNT_TOKEN__ placeholder (Canal/Flannel-Calico deployments), the installer substitutes the live Kubernetes ServiceAccount bearer token before logging, exposing the token to any authenticated user with pods/log permission in the namespace with calico-node. The token holds patch privileges on pods/status, enabling annotation-based attacks against cluster workloads. The default kubeconfig-based authentication path is not affected. This is a direct regression of TTA-2018-001.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41184.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41184
- https://www.tigera.io/security-bulletins/tta-2026-001/
- https://github.com/projectcalico/calico/pull/12502
- https://github.com/projectcalico/calico/pull/12526
- https://github.com/projectcalico/calico/pull/12527
