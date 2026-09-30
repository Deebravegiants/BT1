# [H] TShock Security Escalation Exploit

## Summary
Severity: High
Advisory: GHSA-hvm9-wc8j-mgrc
CWE: CWE-305, CWE-613, CWE-863
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:L/SI:H/SA:H (CVSS_V4)
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-hvm9-wc8j-mgrc
Type: github-advisory

## Affected
- NuGet: `TShock` — affected >=4.3.21 <5.2.1

## Details
### Impact
An issue with the way OTAPI manages client connections results in stale UUIDs remaining on `RemoteClient` instances after a player disconnects.

Because of this, if the following conditions are met a player may assume the login state of a previously connected player:
1. The server has UUID login enabled
2. An authenticated player disconnects
3. A subsequent player connects with a modified client that does not send the `ClientUUID#68` packet during connection
4. The server assigns the same `RemoteClient` object that belonged to the originally authenticated player to the newly connected player


### Patches
TShock 5.2.1 hotfixes this issue. A more robust fix will be made to OTAPI itself.

### Workarounds
Implement a RemoteClient reset event handler in a plugin like so:
```csharp
public override void Initialize()
{
        On.Terraria.RemoteClient.Reset += RemoteClient_Reset;
}

private static void RemoteClient_Reset(On.Terraria.RemoteClient.orig_Reset orig, RemoteClient client)
{
	client.ClientUUID = null;
        orig(client);
}
```

## References
- https://github.com/Pryaxis/TShock/security/advisories/GHSA-hvm9-wc8j-mgrc
- https://github.com/Pryaxis/TShock/commit/5075997264b48e27960e3446a948ecb0ea0f5a03
- https://github.com/Pryaxis/TShock
