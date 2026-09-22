# [H] GlPI-Agent MSI package installation doesn't update folder security profile when using non default installation folder

## Summary
Severity: High
Advisory: CVE-2024-28241
Aliases: GHSA-3268-p58w-86hw
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-28241
Type: osv

## Details
The GLPI Agent is a generic management agent. Prior to version 1.7.2, a local user can modify GLPI-Agent code or used DLLs to modify agent logic and even gain higher privileges. Users should upgrade to GLPI-Agent 1.7.2 to receive a patch. As a workaround, use the default installation folder which involves installed folder is automatically secured by the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28241.json
- https://github.com/glpi-project/glpi-agent/security/advisories/GHSA-3268-p58w-86hw
- https://nvd.nist.gov/vuln/detail/CVE-2024-28241
- https://github.com/glpi-project/glpi-agent/commit/9a97114f595562c91b0833b4a800dd51e9df65e9
