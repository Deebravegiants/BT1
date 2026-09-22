# [C] Frogman: Dialplan template parameters interpolated into extensions_custom.conf without escaping

## Summary
Severity: Critical
Advisory: CVE-2026-46512
Aliases: GHSA-pxfc-q72v-jh8m
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-46512
Type: osv

## Details
Frogman provides headless PBX control through MCP and HTTP API. Prior to 1.6.2, fm_dialplan_apply accepted template parameters including greeting, dest, url, extension, code, and file, and Tools/DialplanApply.php wrote Dialplan/Templates.php output to extensions_custom.conf while only Dialplan/TemplateBase.php:38-42 sanitized contextName(), allowing a PERM_WRITE caller using confirm:true to inject arbitrary Asterisk directives such as System(), Set(SHELL(...)), Goto, or Macro. This issue is fixed in version 1.6.2.

## References
- https://github.com/mwtcmi/frogman/releases/tag/v1.6.1
- https://github.com/mwtcmi/frogman/releases/tag/v1.6.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46512.json
- https://github.com/mwtcmi/frogman/security/advisories/GHSA-pxfc-q72v-jh8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-46512
- https://github.com/mwtcmi/frogman/commit/36a05ffa2df1d256b6f6f7c3b66ef77ebe3e458a
