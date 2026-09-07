# [H] PocketMine-MP vulnerable to server crash with certain invalid JSON payloads in `LoginPacket` due to vulnerable dependency

## Summary
Severity: High
Advisory: GHSA-pqp3-8rrw-g8vm
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-pqp3-8rrw-g8vm
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <4.20.5
- Packagist: `pocketmine/pocketmine-mp` — affected >=4.21.0 <4.21.1

## Details
### Impact
An attacker could crash PocketMine-MP by sending malformed JSON in `LoginPacket`.

This happened due to a bug in [`netresearch/jsonmapper`](https://github.com/cweiske/JsonMapper). The library wasn't doing proper checks when mapping JSON arrays and objects onto scalar model properties such as strings.

### Patches
The problem was fixed in a fork of JsonMapper in dktapps/JsonMapper@a31902a31f5b6fdb832f57c0e3a3f16a3b41c012. PocketMine-MP releases 4.20.5 and 4.21.1 have been released with the fix.

### Workarounds
- Users of PocketMine-MP source installations may manually install the patched version of JsonMapper by backporting commit pmmp/PocketMine-MP@09668a37d66c6023685a948b7550c918620e98f2.
- A plugin may also be able to workaround this issue by using `DataPacketReceiveEvent` to attempt detection of suspicious payloads. An `ErrorException` will be thrown in the crash case, which can be caught by plugins.

### References
cweiske/jsonmapper#210

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-pqp3-8rrw-g8vm
- https://github.com/cweiske/jsonmapper/pull/210
- https://github.com/pmmp/PocketMine-MP/commit/09668a37d66c6023685a948b7550c918620e98f2
- https://github.com/pmmp/netresearch-jsonmapper/commit/a31902a31f5b6fdb832f57c0e3a3f16a3b41c012
- https://github.com/pmmp/PocketMine-MP
