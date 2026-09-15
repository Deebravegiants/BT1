# [H] Wazuh 4.0.0 < 4.14.6 Path Traversal Arbitrary Directory Deletion via Cluster Hello

## Summary
Severity: High
Advisory: CVE-2026-74044
Aliases: GHSA-f34r-fcjf-qx6j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-74044
Type: osv

## Details
Wazuh 4.0.0 before 4.14.6 contains a path traversal vulnerability that allows authenticated cluster peers to delete arbitrary directory contents by supplying a traversal-shaped node name in the cluster hello payload without validation. Attackers holding a valid cluster Fernet key can craft a malicious node name and disconnect, triggering the master's peer cleanup routine to remove the contents of arbitrary directories within the Wazuh installation path writable by the wazuh user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74044.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-f34r-fcjf-qx6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-74044
- https://www.vulncheck.com/advisories/wazuh-path-traversal-arbitrary-directory-deletion-via-cluster-hello
- https://github.com/wazuh/wazuh/pull/36460
- https://github.com/wazuh/wazuh
