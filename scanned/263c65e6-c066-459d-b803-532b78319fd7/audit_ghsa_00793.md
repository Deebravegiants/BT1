# [H] Remote Code Execution in Red Discord Bot

## Summary
Severity: High
Advisory: GHSA-7257-96vg-qf6x
CVE: CVE-2020-15147
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-21
Source: https://github.com/advisories/GHSA-7257-96vg-qf6x
Type: github-advisory

## Affected
- PyPI: `Red-DiscordBot` — affected >=0 <3.3.12

## Details
### Impact
A RCE exploit has been discovered in the Streams module: this exploit allows Discord users with specifically crafted "going live" messages to inject code into the Streams module's going live message. By abusing this exploit, it's possible to perform destructive actions and/or access sensitive information.

### Patches
This critical exploit has been fixed on version ``3.3.12`` & ``3.4``.

### Workarounds
Unloading the Streams module with ``unload streams`` can render this exploit not accessible. We still highly recommend updating to ``3.3.12`` or ``3.4`` to completely patch this issue.

### References
* https://github.com/Cog-Creators/Red-DiscordBot/pull/4183

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Cog-Creators/Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot)
* Over on our [Discord server](https://discord.gg/red)

## References
- https://github.com/Cog-Creators/Red-DiscordBot/security/advisories/GHSA-7257-96vg-qf6x
- https://nvd.nist.gov/vuln/detail/CVE-2020-15147
- https://github.com/Cog-Creators/Red-DiscordBot/pull/4183
- https://github.com/Cog-Creators/Red-DiscordBot/pull/4183/commits/e269ea0d3bc88417163c18431b1df38a9be92bfc
- https://github.com/Cog-Creators/Red-DiscordBot
- https://github.com/pypa/advisory-database/tree/main/vulns/red-discordbot/PYSEC-2020-266.yaml
