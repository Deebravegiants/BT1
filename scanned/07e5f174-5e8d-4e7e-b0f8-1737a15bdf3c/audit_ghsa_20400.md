# [H] Unhandled exception when decoding form response JSON

## Summary
Severity: High
Advisory: GHSA-wjfq-88q2-r34j
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-wjfq-88q2-r34j
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=4.0.0 <4.0.7

## Details
### Impact
When handling form responses from the client (`ModalFormResponsePacket`), the Minecraft Windows client may send weird JSON that `json_decode()` can't understand. A workaround for this is implemented in `InGamePacketHandler::stupid_json_decode()`.

An `InvalidArgumentException` is thrown by this function when it fails to fix an error found in the JSON, which is not caught by the caller. This leads to a server crash.

### Patches
56fe71d939c38fe14e18a31a673a9331bcc0e4ca

### Workarounds
A plugin may handle `DataPacketReceiveEvent`, capture `ModalFormResponsePacket` and run the provided JSON through `stupid_json_decode`.

Note that this requires copying the body of the function to a plugin, since the function is currently private.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-wjfq-88q2-r34j
- https://github.com/pmmp/PocketMine-MP/commit/56fe71d939c38fe14e18a31a673a9331bcc0e4ca
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/4.0.7/changelogs/4.0.md#407
