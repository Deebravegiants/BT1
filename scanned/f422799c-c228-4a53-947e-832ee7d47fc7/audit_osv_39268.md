# [H] Wazuh Cluster DAPI Protocol Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-44901
Aliases: GHSA-8c6v-7g3w-prrq
CVSS: 8.4 (CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-44901
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.0.0 until 4.14.6 and 5.0.0-beta2, AffectedItemsWazuhResult.merge() in framework/wazuh/core/results.py trusts the sort_casting field in a cluster worker's JSON response. During a distributed API merge, attacker-controlled type names are resolved through Python builtins without an allowlist. A compromised worker can set sort_casting to exec and place Python source in affected_items, causing the master to execute the payload as root when responses from multiple nodes are merged. This issue is fixed in versions 4.14.6 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44901.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-8c6v-7g3w-prrq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44901
- https://github.com/wazuh/wazuh/commit/b29849f8abb08d78f257e6106b6111a8a1b0e621
- https://github.com/wazuh/wazuh/pull/35757
