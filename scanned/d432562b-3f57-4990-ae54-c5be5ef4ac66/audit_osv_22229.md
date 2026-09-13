# [M] Inadequate access verification when using proxy commands in ArchiSteamFarm

## Summary
Severity: Medium
Advisory: CVE-2022-23627
Aliases: GHSA-88ch-366c-5m89
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-02-08
Source: https://osv.dev/vulnerability/CVE-2022-23627
Type: osv

## Details
ArchiSteamFarm (ASF) is a C# application with primary purpose of idling Steam cards from multiple accounts simultaneously. Due to a bug in ASF code, introduced in version V5.2.2.2, the program didn't adequately verify effective access of the user sending proxy (i.e. `[Bots]`) commands. In particular, a proxy-like command sent to bot `A` targeting bot `B` has incorrectly verified user's access against bot `A` - instead of bot `B`, to which the command was originally designated. This in result allowed access to resources beyond those configured, being a security threat affecting confidentiality of other bot instances. A successful attack exploiting this bug requires a significant access granted explicitly by original owner of the ASF process prior to that, as attacker has to control at least a single bot in the process to make use of this inadequate access verification loophole. The issue is patched in ASF V5.2.2.5, V5.2.3.2 and future versions. Users are advised to update as soon as possible.

## References
- https://github.com/JustArchiNET/ArchiSteamFarm/releases/tag/5.2.2.5
- https://github.com/JustArchiNET/ArchiSteamFarm/releases/tag/5.2.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23627.json
- https://github.com/JustArchiNET/ArchiSteamFarm/security/advisories/GHSA-88ch-366c-5m89
- https://nvd.nist.gov/vuln/detail/CVE-2022-23627
- https://github.com/JustArchiNET/ArchiSteamFarm/commit/7a29d9282bdc3280db2a379c24f73916d786f9b4
- https://github.com/JustArchiNET/ArchiSteamFarm/commit/f807bdb660e75dee5a34994f2ea70970ca6d0492
- https://github.com/JustArchiNET/ArchiSteamFarm/pull/2501
- https://github.com/JustArchiNET/ArchiSteamFarm/pull/2509
