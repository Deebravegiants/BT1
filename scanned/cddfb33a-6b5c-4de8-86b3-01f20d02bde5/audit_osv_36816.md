# [H] Kanboard is Missing Access Control on Plugin Installation leading to Administrative RCE

## Summary
Severity: High
Advisory: CVE-2026-25924
Aliases: GHSA-grch-p7vf-vc4f
CVSS: 8.4 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-25924
Type: osv

## Details
Kanboard is project management software focused on Kanban methodology. Prior to 1.2.50, a security control bypass vulnerability in Kanboard allows an authenticated administrator to achieve full Remote Code Execution (RCE). Although the application correctly hides the plugin installation interface when the PLUGIN_INSTALLER configuration is set to false, the underlying backend endpoint fails to verify this security setting. An attacker can exploit this oversight to force the server to download and install a malicious plugin, leading to arbitrary code execution. This vulnerability is fixed in 1.2.50.

## References
- https://github.com/kanboard/kanboard/releases/tag/v1.2.50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25924.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-grch-p7vf-vc4f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25924
- https://github.com/kanboard/kanboard/commit/b9ada89b1a64034612fc4262b88c42458c0d6ee4
