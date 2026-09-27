# [M] Natro Macro: Malicious actions allowed through Discord RC Commands by any user

## Summary
Severity: Medium
Advisory: CVE-2026-28800
Aliases: GHSA-ph9r-2qjm-ghvg
CVSS: 6.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-28800
Type: osv

## Details
Natro Macro is an open-source Bee Swarm Simulator macro written in AutoHotkey. Prior to version 1.1.0, anyone with Discord Remote Control set up in a non-private channel gives access to any user with the permission to send message in said channel access to do anything on their computer. This includes keyboard and mouse inputs and full file access. This issue has been patched in version 1.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28800.json
- https://github.com/NatroTeam/NatroMacro/security/advisories/GHSA-ph9r-2qjm-ghvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-28800
