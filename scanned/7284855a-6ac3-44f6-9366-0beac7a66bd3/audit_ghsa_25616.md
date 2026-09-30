# [M] Exposure of Sensitive Information to an Unauthorized Actor in DisCatSharp

## Summary
Severity: Medium
Advisory: GHSA-frxg-hf44-q765
CVE: CVE-2022-24849
CWE: CWE-200
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-frxg-hf44-q765
Type: github-advisory

## Affected
- NuGet: `DisCatSharp` — affected >=9.8.5 <9.9.1

## Details
### Impact
Users of versions 9.8.5, 9.8.6, 9.9.0 and previously published prereleases of 10.0.0 who have used either one of the two `RequireDisCatSharpDeveloperAttribute`s or the `BaseDiscordClient.LibraryDeveloperTeam` have potentially had their bot token sent to a web server not affiliated with Discord. This server is owned and operated by DisCatSharp's development team. The tokens were not logged, yet it is still advisable to reset the tokens of potentially affected bots.

### Patches
9.9.1 has been released to patch the issue for the current stable release and the current 10.0.0 prereleases are also no longer affected.

### Workarounds
Remove all uses of the two `RequireDisCatSharpDeveloperAttribute`s and all direct calls to `BaseDiscordClient.LibraryDeveloperTeam`.

### Details
The `HttpClient` responsible for sending requests to the Discord API was erroneously reused to send requests to our website when DisCatSharp's team members were to be fetched.

### For more information
If you have any questions or comments about this advisory:
* Join our [Discord server](https://discord.gg/GGYSywkxwN)
* Email us at [ottero@aitsys.dev](mailto:ottero@aitsys.dev)

## References
- https://github.com/Aiko-IT-Systems/DisCatSharp/security/advisories/GHSA-frxg-hf44-q765
- https://nvd.nist.gov/vuln/detail/CVE-2022-24849
- https://github.com/Aiko-IT-Systems/DisCatSharp
