# [M] PocketMine-MP vulnerable to denial-of-service by sending large modal form responses

## Summary
Severity: Medium
Advisory: GHSA-7m9r-rq9j-wmmh
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-7m9r-rq9j-wmmh
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.12.5

## Details
### Impact
Due to a workaround for an old client bug (which has since been fixed), very large JSON payloads in `ModalFormResponsePacket` were able to cause the server to spend a significant amount of time processing the packet. Large numbers of these packets were able to hog CPU time so as to prevent the server from processing other connections in a timely manner.

### Patches
The problem has been addressed in 3baa5ab71214f96e6e7ab12cb9beef08118473b5 by removing the workaround code.

### Workarounds
Plugins could cancel `DataPacketReceiveEvent` for this packet, decode the data their way, and then call `Player->onFormSubmit()` directly, bypassing the vulnerable code.

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-7m9r-rq9j-wmmh
- https://github.com/pmmp/PocketMine-MP
