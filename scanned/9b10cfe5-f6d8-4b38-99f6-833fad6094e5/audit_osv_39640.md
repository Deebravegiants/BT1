# [C] Wazuh: Arbitrary File Deletion via Cluster Protocol – Incomplete Path Validation in end_receiving_file()

## Summary
Severity: Critical
Advisory: CVE-2026-46343
Aliases: GHSA-cqvw-w2rg-327f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:L/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-46343
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.0.0 until 4.14.6 and 5.0.0-beta2, WazuhCommon.end_receiving_file() in framework/wazuh/core/cluster/common.py allows a cluster-authenticated node to delete files outside WAZUH_PATH. A syn_i_w_m_e request with an unknown task_id reaches the cleanup branch, where an attacker-controlled filename is passed to os.path.join without canonicalization or confinement. Absolute paths and traversal sequences can therefore target files such as ossec.conf, jwt_secret.json, TLS certificates, and ruleset files that are accessible to the Wazuh manager process. Deletion can disable the manager, invalidate API tokens, or disrupt cluster and API connectivity. This issue is fixed in versions 4.14.6 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46343.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-cqvw-w2rg-327f
- https://nvd.nist.gov/vuln/detail/CVE-2026-46343
- https://github.com/wazuh/wazuh/commit/90d43547d166cdbe65e9a3d011f946214df9179c
- https://github.com/wazuh/wazuh/pull/36060
