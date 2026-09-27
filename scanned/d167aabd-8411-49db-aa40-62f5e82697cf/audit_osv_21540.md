# [M] CVE-2021-43819

## Summary
Severity: Medium
Advisory: CVE-2021-43819
Aliases: GHSA-64r2-hfr9-849j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2021-43819
Type: osv

## Details
Stargate-Bukkit is a mod for the minecraft video game which adds a portal focused environment. In affected versions Minecarts with chests will drop their items when teleporting through a portal; when they reappear, they will still have their items impacting the integrity of the game world. The teleport code has since been rewritten and is available in release `0.11.5.1`. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/stargate-bukkit/Stargate-Bukkit/security/advisories/GHSA-64r2-hfr9-849j
