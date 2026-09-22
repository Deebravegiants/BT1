# [M] Wazuh before 5.0.0-beta3 Cluster Attribution Spoofing via Inventory Sync

## Summary
Severity: Medium
Advisory: CVE-2026-67307
Aliases: GHSA-jv5p-fhwh-9w55
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67307
Type: osv

## Details
Wazuh 5.0.0-beta1 (fixed in 5.0.0-beta3) does not validate or override the cluster_name and cluster_node fields in inventory-sync Start FlatBuffer messages, while validating only the agentid against the authenticated agent identity. This allows a low-privileged enrolled agent to spoof cluster attribution in indexed inventory and vulnerability documents by forging wazuh.cluster.name values and influencing the document _id prefix, potentially tampering with inventory records or, in shared-indexer multi-cluster deployments, poisoning another cluster's records when numeric agent IDs collide.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67307.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-jv5p-fhwh-9w55
- https://nvd.nist.gov/vuln/detail/CVE-2026-67307
- https://www.vulncheck.com/advisories/wazuh-before-beta3-cluster-attribution-spoofing-via-inventory-sync
- https://github.com/wazuh/wazuh/commit/b3dae02ec9ddcfd449cb61b4c76d180e3e43f79a
