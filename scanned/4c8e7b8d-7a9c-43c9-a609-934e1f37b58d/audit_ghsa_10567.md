# [M] PocketMine-MP has LogDoS by many junk properties in client data JWT in LoginPacket

## Summary
Severity: Medium
Advisory: GHSA-xp4f-g2cm-rhg7
CWE: CWE-779
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-xp4f-g2cm-rhg7
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.42.1

## Details
### Impact

Attackers can fill the body of the clientData JWT in LoginPacket with lots of junk properties, causing the server to flood warning messages, as well as wasting CPU time.

This happens because the JsonMapper instance used to process the JWT body is configured to warn on unexpected properties instead of rejecting them outright. While this behaviour increases flexibility for random changes introduced by Microsoft, it also creates vulnerabilities if not handled carefully.

This vulnerability affects PocketMine-MP servers exposed to a public network where unknown actors may have access.

### Patches

This issue was fixed in c1d4a813fb8c21bfd8b9affd040da864b794df71 by restricting the number of unknown properties to 10, and rejecting the packet if this limit is exceeded. This continues to tolerate random additions to the JWT between versions, while preventing the logger from being abused by clients to slow down the server.

### Workarounds
Plugins can handle `DataPacketReceiveEvent` to capture `LoginPacket`, and pre-process the clientData JWT to ensure it doesn't have any unusual properties in it. This can be achieved using `JsonMapper` (see the original affected code below) and setting the `bExceptionOnUndefinedProperty` flag to `true`. A `JsonMapper_Exception` will be thrown if the JWT is problematic.

However, it's important to caveat that this approach may cause login failures if any unexpected properties appear out of the blue in future versions (which has happened in the past).

### References
Affected code:

https://github.com/pmmp/PocketMine-MP/blob/5.41.1/src/network/mcpe/handler/LoginPacketHandler.php#L289-L303
https://github.com/pmmp/PocketMine-MP/blob/5.41.1/src/network/mcpe/handler/LoginPacketHandler.php#L334-L350

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-xp4f-g2cm-rhg7
- https://github.com/pmmp/PocketMine-MP/commit/c1d4a813fb8c21bfd8b9affd040da864b794df71
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/5.41.1/src/network/mcpe/handler/LoginPacketHandler.php#L289-L303
- https://github.com/pmmp/PocketMine-MP/blob/5.41.1/src/network/mcpe/handler/LoginPacketHandler.php#L334-L350
