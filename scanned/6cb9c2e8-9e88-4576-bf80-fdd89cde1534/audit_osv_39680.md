# [H] Frogman: Multiple read-tier tools expose admin-grade data and arbitrary GraphQL execution

## Summary
Severity: High
Advisory: CVE-2026-46515
Aliases: GHSA-q4c4-5cr4-8q47
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46515
Type: osv

## Details
Frogman provides headless PBX control through MCP and HTTP API. Prior to 1.6.3, PERM_READ access was sufficient to call fm_list_managers, fm_list_pinsets, fm_show_context, fm_get_mcp_config, fm_backup_status, fm_whos_calling, fm_run_saved_query, and fm_diagnose_trunk, exposing AMI manager secrets, outbound dial PINs, full Asterisk dialplan context, root SSH connection commands, backup artifact paths, CDR history, arbitrary saved GraphQL query execution, and raw AMI endpoint dumps containing SIP fields such as password, md5_cred, and oauth_secret. This issue is fixed in version 1.6.3.

## References
- https://github.com/mwtcmi/frogman/releases/tag/v1.6.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46515.json
- https://github.com/mwtcmi/frogman/security/advisories/GHSA-q4c4-5cr4-8q47
- https://nvd.nist.gov/vuln/detail/CVE-2026-46515
- https://github.com/mwtcmi/frogman/issues/13
- https://github.com/mwtcmi/frogman/issues/25
- https://github.com/mwtcmi/frogman/commit/55ea257d5c24bc01c814a607faa7e76e86b111ec
- https://github.com/mwtcmi/frogman/commit/b8a8bfc12b564bcb77caef952873b9ffd4a98b00
