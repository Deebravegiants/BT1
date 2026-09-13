# [M] Denial-of-service vulnerability processing large chat messages containing many newlines

## Summary
Severity: Medium
Advisory: GHSA-gj94-v4p9-w672
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-gj94-v4p9-w672
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.2.10

## Details
### Impact
PocketMine-MP caps maximum chat message length at 512 Unicode characters, or about 2048 bytes. No more than 2 chat messages may be sent per tick. However, due to legacy reasons, incoming chat message blobs are split by `\n`, and each part is treated as a separate message, the length of each part is individually checked. The length of the whole message is not checked.

This leads to an exploitable performance issue, in which a malicious client may send a chat packet of several megabytes containing nothing but `\n` newline characters. The server will parse this into a very large array and spend a long time (several milliseconds) iterating over it for no reason.

Furthermore, due to the lack of sufficient rate limit checks before parsing messages, malicious clients may bombard the server with many thousands of these malicious messages, causing lockups for a significant amount of time (seconds or minutes).

### Patches
This bug was addressed in https://github.com/pmmp/PocketMine-MP/commit/df33e179e5d3ff13b56a2d7060bf592b0f797258 by:
- checking the length of the incoming message as a whole before parsing it - it may not be larger than `messageCounter * maxChatMessageSize` (`messageCounter` is decremented once for every message sent)
- limiting the maximum number of times a message may be split on newlines before giving up and discarding the message (maximum 3 parts; anything after the first 2 parts is discarded)

### Workarounds
Handle `DataPacketReceiveEvent` and check for these excessive newlines in incoming `TextPacket`.

### For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-gj94-v4p9-w672
- https://github.com/pmmp/PocketMine-MP
