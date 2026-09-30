# [C] Blueprint Studio Git credential helper command injection

## Summary
Severity: Critical
Advisory: CVE-2026-53455
Aliases: GHSA-wjpc-mc3f-w5rg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-53455
Type: osv

## Details
Blueprint Studio is a VS Code-like file editor for Home Assistant configuration files. Prior to 2.5.2, Blueprint Studio generated a shell-based Git credential helper in custom_components/blueprint_studio/backend/git_manager.py by interpolating the configured Git username and token directly into executable helper script content without validating credential values. An attacker able to set Git credentials could include newline characters or shell syntax in a username or token. When Git executed the generated credential helper, the injected shell commands ran with the operating-system privileges of Home Assistant and could access or modify Home Assistant configuration data. This issue is fixed in version 2.5.2.

## References
- https://github.com/ha-china/blueprint-studio/releases/tag/v2.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53455.json
- https://github.com/ha-china/blueprint-studio/security/advisories/GHSA-wjpc-mc3f-w5rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-53455
- https://github.com/ha-china/blueprint-studio/commit/943aed0be67f3a910b0f70a3864288d5e17e55ce
