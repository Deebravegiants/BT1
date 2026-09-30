# [M] LibreChat has Insufficient Access Control for Agent Permission Queries

## Summary
Severity: Medium
Advisory: CVE-2025-69221
Aliases: GHSA-5ccx-4r3h-9qc7
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-69221
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. Version 0.8.1-rc2 does not enforce proper access control when
querying agent permissions. An authenticated attacker can read the permissions of arbitrary agents, even if they have no permissions for this agent. LibreChat allows the configuration of agents that have a predefined set of instructions and context. Private agents are not visible to other users. However, if an attacker knows the agent ID, they can read the permissions of the agent including the permissions individually assigned to other users. This issue is fixed in version 0.8.2-rc2.

## References
- https://github.com/danny-avila/LibreChat/releases/tag/v0.8.2-rc2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69221.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-5ccx-4r3h-9qc7
- https://nvd.nist.gov/vuln/detail/CVE-2025-69221
- https://github.com/danny-avila/LibreChat/commit/06ba025bd95574c815ac6968454be7d3b024391c
