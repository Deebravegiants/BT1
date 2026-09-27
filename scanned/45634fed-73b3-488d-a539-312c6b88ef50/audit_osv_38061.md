# [C] Sandboxie-Plus privilege escalation via INI CRLF injection bypassing EditAdminOnly

## Summary
Severity: Critical
Advisory: CVE-2026-34458
Aliases: GHSA-6xqg-2cjq-95qf
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-34458
Type: osv

## Details
Sandboxie-Plus is an open source sandbox-based isolation software for Windows. In versions 1.17.2 and earlier, an INI injection vulnerability allows any standard local user to bypass configuration restrictions (EditAdminOnly and ConfigPassword) and inject arbitrary directives into the global Sandboxie.ini configuration file. The background service skips authorization checks for IPC messages targeting sections beginning with UserSettings_, but does not sanitize CRLF characters in either the value parameter (via MSGID_SBIE_INI_ADD_SETTING) or the setting name parameter (via MSGID_SBIE_INI_SET_SETTING). An attacker can inject a new sandbox section header with unrestricted permissions, enabling sandbox escape and SYSTEM privilege escalation. This issue has been fixed in version 1.17.3.

## References
- https://github.com/sandboxie-plus/Sandboxie/releases/tag/v1.17.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34458.json
- https://github.com/sandboxie-plus/Sandboxie/security/advisories/GHSA-6xqg-2cjq-95qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34458
