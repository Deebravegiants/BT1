# [H] Improper Authentication

## Summary
Severity: High
Advisory: GHSA-qxx8-292g-2w66
CWE: CWE-287
Ecosystem: NuGet
Published: 2021-03-08
Source: https://github.com/advisories/GHSA-qxx8-292g-2w66
Type: github-advisory

## Affected
- NuGet: `Microsoft.Bot.Connector` — affected >=4.6.0 <4.6.4
- NuGet: `Microsoft.Bot.Connector` — affected >=4.7.0 <4.7.3
- NuGet: `Microsoft.Bot.Connector` — affected >=4.8.0 <4.8.2
- NuGet: `Microsoft.Bot.Connector` — affected >=4.9.0 <4.9.5
- NuGet: `Microsoft.Bot.Connector` — affected >=4.10.0 <4.10.3

## Details
### Impact
A maliciously crafted claim may be incorrectly authenticated by the bot. Impacts bots that are not configured to be used as a Skill. This vulnerability requires an an attacker to have internal knowledge of the bot.

### Patches
The problem has been patched in all affected versions. Please see the list of patched versions for the most appropriate one for your individual case.

### Workarounds
Users who do not wish or are not able to upgrade can add an authentication configuration containing ClaimsValidator which throws an exception if the Claims are Skill Claims.

For detailed instructions, see the link in the References section.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Microsoft Bot Builder SDK](https://github.com/microsoft/botbuilder-dotnet)
* Email us at [bf-reports@microsoft.com](mailto:bf-reports@microsoft.com)

## References
- https://github.com/microsoft/botbuilder-dotnet/security/advisories/GHSA-qxx8-292g-2w66
- https://aka.ms/SkillClaimsValidationDotnet
- https://www.nuget.org/packages/Microsoft.Bot.Connector
