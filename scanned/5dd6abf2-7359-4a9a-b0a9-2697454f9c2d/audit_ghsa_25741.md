# [H] NaN/INF in serverbound movement packets can crash clients and servers

## Summary
Severity: High
Advisory: GHSA-fm35-jgg3-3grx
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-fm35-jgg3-3grx
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <3.18.1

## Details
### Impact
A malicious client may send a `MovePlayerPacket` to the server whose position or rotation contains NaN or INF. Since neither the server nor vanilla client handles this properly, a number of interesting side effects come into play.

- The server may crash in various ways if this exploit is used, because some mathematical operations on NaN/INF generate PHP warnings, which are converted into exceptions.
- Clients may not be able to see other clients who have a NaN/INF rotation.
- Clients may also crash in such cases.

### Patches
A patch for this was included in the 3.18.1 release: https://github.com/pmmp/PocketMine-MP/commit/fb20bb38327b4c08ee3976640cd0dd547388a638

### Workarounds
Workarounds could be implemented as plugins using `DataPacketReceiveEvent` to block any inbound movement packets containing bogus values.

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [pmmp/PocketMine-MP](https://github.com/pmmp/PocketMine-MP)
- Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-fm35-jgg3-3grx
