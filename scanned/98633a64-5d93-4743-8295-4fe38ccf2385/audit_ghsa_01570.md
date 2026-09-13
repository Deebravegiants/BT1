# [M] Unauthorized privilege escalation in Mod module

## Summary
Severity: Medium
Advisory: GHSA-mp9m-g7qj-6vqr
CVE: CVE-2020-15278
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-mp9m-g7qj-6vqr
Type: github-advisory

## Affected
- PyPI: `Red-DiscordBot` — affected >=0 <3.4.1

## Details
### Impact
An unauthorized privilege escalation exploit has been discovered in the Mod module: this exploit allows Discord users with a high privilege level within the guild to bypass hierarchy checks when the application is in a specific condition that is beyond that user's control. By abusing this exploit, it's possible to perform destructive actions within the guild the user has high privileges in.

### Patches
This exploit has been fixed on version & ``3.4.1``.

### Workarounds
Unloading the Mod module with ``unload mod`` __or__, disabling the ``massban`` command with ``command disable global massban`` can render this exploit not accessible. We still highly recommend updating to ``3.4.1`` to completely patch this issue.

### References
* https://github.com/Cog-Creators/Red-DiscordBot/commit/726bfd38adfdfaef760412a68e01447b470f438b

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Cog-Creators/Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot)
* Over on our [Discord server](https://discord.gg/red)

## References
- https://github.com/Cog-Creators/Red-DiscordBot/security/advisories/GHSA-mp9m-g7qj-6vqr
- https://nvd.nist.gov/vuln/detail/CVE-2020-15278
- https://github.com/Cog-Creators/Red-DiscordBot/commit/726bfd38adfdfaef760412a68e01447b470f438b
- https://github.com/Cog-Creators/Red-DiscordBot
- https://github.com/Cog-Creators/Red-DiscordBot/releases/tag/3.4.1
- https://github.com/pypa/advisory-database/tree/main/vulns/red-discordbot/PYSEC-2020-267.yaml
