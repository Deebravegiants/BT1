# [H] Buffer length underflow in LoginPacket causing unchecked exceptions to be thrown

## Summary
Severity: High
Advisory: GHSA-5jfw-35xp-5m42
CWE: CWE-124
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-5jfw-35xp-5m42
Type: github-advisory

## Affected
- Packagist: `pocketmine/bedrock-protocol` — affected >=0 <8.0.2

## Details
### Impact
`LoginPacket` uses `BinaryStream->getLInt()` to read the lengths of JSON payloads it wants to decode. Unfortunately, `BinaryStream->getLInt()` returns a signed integer, meaning that a malicious client can craft a packet with a large uint32 value for payload buffer size (which would be interpreted as a negative signed int32), causing `BinaryStream->get()` to throw an exception.

In the context of PocketMine-MP, this leads to a server crash when the vulnerability is exploited.

### Patches
e3fce7632b94e83fd6a518a87dcaf6a11681c4ac

### Workarounds
This can be worked around by registering a custom `LoginPacket` implementation into `PacketPool` which overrides [this code](https://github.com/pmmp/BedrockProtocol/blob/47532c95ea37d5f0365b23f734d70d943ff95295/src/LoginPacket.php#L54) to patch it.

### For more information
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/BedrockProtocol/security/advisories/GHSA-5jfw-35xp-5m42
- https://github.com/pmmp/BedrockProtocol/commit/e3fce7632b94e83fd6a518a87dcaf6a11681c4ac
- https://github.com/pmmp/BedrockProtocol
