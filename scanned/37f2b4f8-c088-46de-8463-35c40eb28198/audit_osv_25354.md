# [H] Remote inventory task command injection when using ssh command mode

## Summary
Severity: High
Advisory: CVE-2023-34254
Aliases: GHSA-39vc-hxgm-j465
CVSS: 7.6 (CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-34254
Type: osv

## Details
The GLPI Agent is a generic management agent. Prior to version 1.5, if glpi-agent is running remoteinventory task against an Unix platform with ssh command, an administrator user on the remote can manage to inject a command in a specific workflow the agent would run with the privileges it uses. In the case, the agent is running with administration privileges, a malicious user could gain high privileges on the computer glpi-agent is running on. A malicious user could also disclose all remote accesses the agent is configured with for remoteinventory task. This vulnerability has been patched in glpi-agent 1.5.

## References
- https://github.com/glpi-project/glpi-agent/blob/dd313ee0914becf74c0e48cb512765210043b478/Changes#L98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34254.json
- https://github.com/glpi-project/glpi-agent/security/advisories/GHSA-39vc-hxgm-j465
- https://nvd.nist.gov/vuln/detail/CVE-2023-34254
