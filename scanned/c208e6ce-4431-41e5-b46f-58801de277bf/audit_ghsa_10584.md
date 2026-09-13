# [H] PocketMine-MP: LogDoS by large complex unknown property logging in clientData in LoginPacket

## Summary
Severity: High
Advisory: GHSA-h6rj-3m53-887h
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-h6rj-3m53-887h
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.41.1

## Details
### Impact

Attackers can put large and/or complex structures as a value to an unknown property in the clientData JWT body in the Minecraft `LoginPacket`, causing the server to generate very long log messages.
Additionally, the property name is logged without any length limitations or sanitization, which can also be abused for LogDoS.

This may be used to spam the log/console, waste CPU time serializing the offending structure, and potentially to crash the server entirely.

This happens because the JsonMapper instance used to process the JWT body is configured to warn on unexpected properties instead of rejecting them outright. While this behaviour increases flexibility for random changes introduced by Microsoft, it also creates vulnerabilities if not handled carefully.

This vulnerability affects PocketMine-MP servers exposed to a public network where unknown actors may have access.

### PoC
1. Connect to the server using a custom client.

2. Send a Minecraft `LoginPacket` containing an unexpected JSON property (e.g., invalid_key) within the ClientData.

3. Set the value of invalid_key to a highly recursive or massive object structure (e.g., an array containing millions of elements or deeply nested arrays).

4. The server hits the `warnUndefinedJsonPropertyHandler`, which attempts to var_export the malicious object, leading to an Out-of-Memory crash.

```
A := make([]interface{}, 1)
	ptr := &A
	for i := 0; i < 500; i++ {
		next := make([]interface{}, 1000)
		(*ptr)[0] = next
		ptr = &next
	}
	data := make([]int, 2000000)
	for i := 0; i < 100; i++ {
		data[i] = i
	}
	(*ptr)[0] = data
	d.PlayFabID = A
 ```

### Patches
The issue was addressed in https://github.com/pmmp/PocketMine-MP/commit/87d1c0cea09d972fd4c2fafb84dac2ecab7649f0 by removing the relevant `var_export` and limiting the length of the logged property name to 80 characters.

### Workarounds
Plugins can handle `DataPacketReceiveEvent` to capture `LoginPacket`, and pre-process the clientData JWT to ensure it doesn't have any unusual properties in it. This can be achieved using `JsonMapper` (see the original affected code below) and setting the `bExceptionOnUndefinedProperty` flag to `true`. A `JsonMapper_Exception` will be thrown if the JWT is problematic.

However, it's important to caveat that this approach may cause login failures if any unexpected properties appear out of the blue in future versions (which has happened in the past).

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-h6rj-3m53-887h
- https://github.com/pmmp/PocketMine-MP/commit/87d1c0cea09d972fd4c2fafb84dac2ecab7649f0
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/blob/5.41.0/src/network/mcpe/handler/LoginPacketHandler.php#L288-L302
- https://github.com/pmmp/PocketMine-MP/blob/5.41.0/src/network/mcpe/handler/LoginPacketHandler.php#L333-L349
