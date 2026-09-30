# [C] Wazuh Manager - NDJSON Injection in inventory_sync via Agent-Controlled DataValue.index

## Summary
Severity: Critical
Advisory: CVE-2026-56699
Aliases: GHSA-ff9g-85jq-r3g3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-56699
Type: osv

## Details
Wazuh Manager before 5.0.0-beta3 fails to escape the DataValue.index field when constructing OpenSearch bulk requests, allowing enrolled agents to inject arbitrary NDJSON operations. Attackers can smuggle delete, index, or update operations into bulk requests executed under the manager's admin credentials, enabling document deletion, alert tampering, and cross-agent SIEM state manipulation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56699.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-ff9g-85jq-r3g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-56699
- https://www.vulncheck.com/advisories/wazuh-manager-ndjson-injection-in-inventory-sync-via-agent-controlled-datavalue-index
