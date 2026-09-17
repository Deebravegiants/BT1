# [H] GLPI-Agent's MSI package installation permits local users to change Agent configuration

## Summary
Severity: High
Advisory: CVE-2024-28240
Aliases: GHSA-hx3x-mmqg-h3jp
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-28240
Type: osv

## Details
The GLPI Agent is a generic management agent. A vulnerability that only affects GLPI-Agent installed on windows via MSI packaging can allow a local user to cause denial of agent service by replacing GLPI server url with a wrong url or disabling the service. Additionally, in the case the Deploy task is installed, a local malicious user can trigger privilege escalation configuring a malicious server providing its own deploy task payload. GLPI-Agent 1.7.2 contains a patch for this issue. As a workaround, edit GLPI-Agent related key under `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` and add `SystemComponent` DWORD value setting it to `1` to hide GLPI-Agent from installed applications.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28240.json
- https://github.com/glpi-project/glpi-agent/security/advisories/GHSA-hx3x-mmqg-h3jp
- https://nvd.nist.gov/vuln/detail/CVE-2024-28240
- https://github.com/glpi-project/glpi-agent/commit/41bbb1169e899bd15350a9e2fdbf9269a3b7a14f
