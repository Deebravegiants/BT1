# [M] ServiceAccount token disclosure via Azure IPAM CNI plugin logs

## Summary
Severity: Medium
Advisory: CVE-2026-41185
Aliases: GHSA-m67g-87rx-v42c, GO-2026-5891
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:L)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-41185
Type: osv

## Details
When Calico is configured with the Azure IPAM plugin, the Calico CNI binary mutates the incoming CNI configuration to attach subnet information before delegating to the IPAM plugin. After mutating, the Azure IPAM helper logs the entire unmarshaled configuration map (stdinData) at INFO level to /var/log/calico/cni/cni.log on every CNI ADD and DEL invocation — once per pod scheduled or terminated on the node. When the cluster is deployed using token-based Kubernetes authentication, this log entry contains the ServiceAccount token, client key, and certificate authority in plaintext. Any principal with read access to /var/log/calico/cni/cni.log on a node  can read these logs and extract the credentials, which grant cluster-wide Calico networking admin privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41185.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41185
- https://www.tigera.io/security-bulletins/tta-2026-002/
- https://github.com/projectcalico/calico/pull/12502
- https://github.com/projectcalico/calico/pull/12526
- https://github.com/projectcalico/calico/pull/12527
