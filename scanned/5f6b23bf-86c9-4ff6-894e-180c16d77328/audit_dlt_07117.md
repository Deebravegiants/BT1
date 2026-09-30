# [?] fix: dos protection for NetworkProcessor (#10039)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2026-09-11
Source: https://github.com/ChainSafe/lodestar/commit/60b5607f3ad48212a500b78357a69b349840a890
Type: security-commit

## Details
fix: dos protection for NetworkProcessor (#10039)

**Motivation**

- NetworkProcessor holds unverified messages and was not designed with
DOS protection in mind

**Description**

- only support to buffer up to 5 roots per message slot, this is to
prevent OOM
  - cap it via `bufferedRootsBySlot = new MapDef<Slot, Set<RootHex>>`
- but support up to 32 searched roots per message slot. This is to make
sure the node is always synced by searching for all roots, and we will
penalize peers in UnknownBlockInput per `pruneFinalized()`
- cap it via `searchedRootsBySlot = new MapDef<Slot, MapDef<RootHex,
SearchedRootEntry>>`
- changed data structure
  - awaitingMessagesByBlockRoot is tracked per topic, same to envelope
- unite `unknownBlocksBySlot` and `unknownEnvelopesBySlot `to
`searchedRootsBySlot `so that we can cap roots per slot easier

Closes https://github.com/ethereum-bounty/lodestar/issues/19

**AI Assistance Disclosure**

- created with the help of Claude

---------

Co-authored-by: twoeths <twoeths@users.noreply.github.com>

## Patch
### packages/beacon-node/src/network/processor/index.ts
```diff
@@ -1,6 +1,6 @@
 import {TopicValidatorResult} from "@libp2p/gossipsub";
 import {routes} from "@lodestar/api";
-import {ForkSeq} from "@lodestar/params";
+import {ForkSeq, NUMBER_OF_COLUMNS} from "@lodestar/params";
 import {computeStartSlotAtEpoch} from "@lodestar/state-transition";
 import {RootHex, Slot, SlotRootHex} from "@lodestar/types";
 import {Logger, MapDef, mapValues, sleep} from "@lodestar/utils";
@@ -59,6 +59,36 @@ export type NetworkProcessorOpts = GossipHandlerOpts & {
  */
 const MAX_UNKNOWN_ROOTS_SLOT_CACHE_SIZE = 3;
 
+/**
+ * Max distinct roots we BUFFER messages for, per slot. Kept tight to avoid the OOM
+ * risk. We don't support super forky condition where there are more than this many roots per slot via gossip.
+ */
+export const MAX_BUFFERED_ROOTS_PER_SLOT = 5;
+
+/**
+ * Max distinct roots we emit an unknown-root search for, per slot. Higher than
+ * the buffer budget because:
+ * - in the attack scenario, the genuine root may comes after the first MAX_BUFFERED_ROOTS_PER_SLOT roots
+ * - if we cannot search, we'll penalize peers in UnknownBlockInput, not in NetworkProcessor
+ */
+export const MAX_SEARCHED_ROOTS_PER_SLOT = 32;
+
+/**
+ * Given the same root and topic, we'll ignore messages after the below cap. Each cap is the number of
+ * legitimate messages we expect for one block, plus headroom for some malformed messages that may arrives first
+ * they will be penalized by the gossip handler
+ */
+export const MAX_AWAITING_MESSAGES_PER_ROOT: Partial<Record<GossipType, number>> = {
+  [GossipType.data_column_sidecar]: 2 * NUMBER_OF_COLUMNS,
+  [GossipType.execution_payload]: 2,
+  [GossipType.execution_payload_bid]: 8,
+};
+
+/**
+ * Track the forwarded peers we already emit to UnknownBlockInput sync.
+ */
+type SearchedRootEntry = {blockPeerIds?: Set<PeerIdStr>; envelopePeerIds?: Set<PeerIdStr>};
+
 /**
  * This is respective to gossipsub seenTTL (which is 550 * 0.7 = 385s), also it's respective
  * to beacon_attestation ATTESTATION_PROPAGATION_SLOT_RANGE (32 slots).
@@ -120,6 +150,14 @@ export enum ReprocessRejectReason {
    * There are too many gossip messages that have unknown block root.
    */
   reached_limit = "reached_limit",
+  /**
+   * Too many distinct unknown roots are already tracked for the message's slot (MAX_UNKNOWN_ROOTS_PER_SLOT).
+   */
+  reached_root_limit = "reached_root_limit",
+  /**
+   * Too many gossip messages are already buffered for this (root, topic) (MAX_AWAITING_MESSAGES_PER_ROOT).
+   */
+  reached_topic_limit = "reached_topic_limit",
   /**
    * The awaiting gossip message is pruned per clock slot.
    */
@@ -185,19 +223,21 @@ export class NetworkProcessor {
   private readonly gossipTopicConcurrency: {[K in GossipType]: number};
   private readonly extractBlockSlotRootFns = createExtractBlockSlotRootFns();
   // we may not receive the block for messages like Attestation and SignedAggregateAndProof messages, in that case PendingGossipsubMessage needs
-  // to be stored in this Map and reprocessed once the block comes
-  private readonly awaitingMessagesByBlockRoot: MapDef<RootHex, Set<PendingGossipsubMessage>>;
+  // to be stored in this Map and reprocessed once the block comes. Keyed by topic per root so we can cap
+  // the number of buffered messages per (root, topic) - see MAX_AWAITING_MESSAGES_PER_ROOT.
+  private readonly awaitingMessagesByBlockRoot: MapDef<RootHex, MapDef<GossipType, Set<PendingGossipsubMessage>>>;
   private awaitingBlockMessageCount = 0;
   // we may not receive the payload for messages that require the FULL payload variant to be processed,
   // in that case PendingGossipsubMessage needs to be stored in this Map and reprocessed once the payload comes
-  private readonly awaitingMessagesByPayloadBlockRoot: MapDef<RootHex, Set<PendingGossipsubMessage>>;
+  private readonly awaitingMessagesByPayloadBlockRoot: MapDef<
+    RootHex,
+    MapDef<GossipType, Set<PendingGossipsubMessage>>
+  >;
   private awaitingPayloadMessageCount = 0;
-  private unknownBlocksBySlot = new MapDef<Slot, MapDef<RootHex, Set<PeerIdStr>>>(
-    () => new MapDef<RootHex, Set<PeerIdStr>>(() => new Set())
-  );
-  private unknownEnvelopesBySlot = new MapDef<Slot, MapDef<RootHex, Set<PeerIdStr>>>(
-    () => new MapDef<RootHex, Set<PeerIdStr>>(() => new Set())
+  private searchedRootsBySlot = new MapDef<Slot, MapDef<RootHex, SearchedRootEntry>>(
+    () => new MapDef<RootHex, SearchedRootEntry>(() => ({}))
   );
+  private bufferedRootsBySlot = new MapDef<Slot, Set<RootHex>>(() => new Set());
 
   constructor(
     modules: NetworkProcessorModules,
@@ -222,8 +262,12 @@ export class NetworkProcessor {
     this.chain.emitter.on(routes.events.EventType.executionPayload, this.onPayloadEnvelopeProcessed);
     this.chain.clock.on(ClockEvent.slot, this.onClockSlot);
 
-    this.awaitingMessagesByBlockRoot = new MapDef<RootHex, Set<PendingGossipsubMessage>>(() => new Set());
-    this.awaitingMessagesByPayloadBlockRoot = new MapDef<RootHex, Set<PendingGossipsubMessage>>(() => new Set());
+    this.awaitingMessagesByBlockRoot = new MapDef<RootHex, MapDef<GossipType, Set<PendingGossipsubMessage>>>(
+      () => new MapDef<GossipType, Set<PendingGossipsubMessage>>(() => new Set())
+    );
+    this.awaitingMessagesByPayloadBlockRoot = new MapDef<RootHex, MapDef<GossipType, Set<PendingGossipsubMessage>>>(
+      () => new MapDef<GossipType, Set<PendingGossipsubMessage>>(() => new Set())
+    );
 
     // TODO: Implement queues and priorization for ReqResp incoming requests
     // Listens to NetworkEvent.reqRespIncomingRequest event
@@ -283,9 +327,12 @@ export class NetworkProcessor {
     if (this.chain.seenBlock(root)) {
       return;
     }
-    const peersForRoot = this.unknownBlocksBySlot.getOrDefault(slot);
-    const alreadySearching = peersForRoot.has(root) || this.awaitingMessagesByBlockRoot.has(root);
-    const forwardedPeers = peersForRoot.getOrDefault(root);
+    const entry = this.searchedRootsBySlot.getOrDefault(slot).getOrDefault(root);
+    const alreadySearching = entry.blockPeerIds !== undefined;
+    if (entry.blockPeerIds === undefined) {
+      entry.blockPeerIds = new Set();
+    }
+    const forwardedPeers = entry.blockPeerIds;
 
     // brand-new search always emits (peer may be undefined)
     let shouldEmit = !alreadySearching;
@@ -309,10 +356,12 @@ export class NetworkProcessor {
     if (this.chain.seenPayloadEnvelope(root)) {
       return;
     }
-    const peersForRoot = this.unknownEnvelopesBySlot.getOrDefault(slot);
-    // capture "already searching" BEFORE getOrDefault(root) creates the entry
-    const alreadySearching = peersForRoot.has(root) || this.awaitingMessagesByPayloadBlockRoot.has(root);
-    const forwardedPeers = peersForRoot.getOrDefault(root);
+    const entry = this.searchedRootsBySlot.getOrDefault(slot).getOrDefault(root);
+    const alreadySearching = entry.envelopePeerIds !== undefined;
+    if (entry.envelopePeerIds === undefined) {
+      entry.envelopePeerIds = new Set();
+    }
+    const forwardedPeers = entry.envelopePeerIds;
 
     let shouldEmit = !alreadySearching; // brand-new search always emits (peer may be undefined)
     if (peer !== undefined && !forwardedPeers.has(peer) && forwardedPeers.size < MAX_PEERS_PER_ROOT) {
@@ -374,14 +423,15 @@ export class NetworkProcessor {
     }
 
     message.msgSlot = slot;
+    const peerId = message.propagationSource.toString();
 
     // this determines whether this message needs to wait for a Block or Envelope
-    // a message should only wait for what it voted for, hence we don't want to put it on both queues
+    // a message should only wait for what it voted for, hence we don't want to put it on both queues.
     let preprocessResult: PreprocessResult = {action: PreprocessAction.PushToQueue};
     // no need to check if root is a descendant of the current finalized block, it will be checked once we validate the message if needed
     if (root && !this.chain.forkChoice.hasBlockHexUnsafe(root)) {
       // starting from GLOAS, unknown root from data_column_sidecar also falls into this case
-      this.searchUnknownBlock({slot, root}, BlockInputSource.network_processor, message.propagationSource.toString());
+      this.searchUnknownRoot({slot, root}, true, false, peerId);
       // for beacon_attestation and beacon_aggregate_and_proof messages, this is only temporary.
       // if "index = 1" we need to await for the Envelope instead
       preprocessResult = {action: PreprocessAction.AwaitBlock, root};
@@ -391,40 +441,32 @@ export class NetworkProcessor {
     // we separate the search action from the await action
 
     // beacon_block: proactively search for parent block/envelope across all forks, but never queue.
-    // BlockInputSync handles cascading recovery if the gossip handler throws.
+    // BlockInputSync handles cascading recovery if the gossip handler throws. The parent root differs from
+    // the message root and this message never awaits, so its search flushes inline here (gated by the budget).
     if (topicType === GossipType.beacon_block) {
       const parentRoot = getParentRootFromSignedBeaconBlockSerialized(message.msg.data);
       if (parentRoot) {
+        let searchParentBlock = false;
+        let searchParentEnvelope = false;
         if (ForkSeq[fork] >= ForkSeq.gloas) {
           // GLOAS: also check parent envelope, same logic as execution_payload_bid
           const parentBlockHash = getParentBlockHashFromGloasSignedBeaconBlockSerialized(message.msg.data);
           if (parentBlockHash && !this.chain.forkChoice.getBlockHexAndBlockHash(parentRoot, parentBlockHash)) {
             const protoBlock = this.chain.forkChoice.getBlockHexDefaultStatus(parentRoot);
             if (protoBlock === null) {
-              this.searchUnknownBlock(
-                {slot, root: parentRoot},
-                BlockInputSource.network_processor,
-                message.propagationSource.toString()
-              );
+              searchParentBlock = true;
             } else if (
               protoBlock.executionPayloadBlockHash &&
               protoBlock.executionPayloadBlockHash !== parentBlockHash
             ) {
               // only search for the envelope by block root if we're sure there is one. Otherwise UnknownBlockSync will penalize the peer.
-              this.searchUnknownEnvelope(
-                {slot, root: parentRoot},
-                BlockInputSource.network_processor,
-                message.propagationSource.toString()
-              );
+              searchParentEnvelope = true;
             }
           }
         } else if (!this.chain.forkChoice.hasBlockHexUnsafe(parentRoot)) {
-          this.searchUnknownBlock(
-            {slot, root: parentRoot},
-            BlockInputSource.network_processor,
-            message.propagationSource.toString()
-          );
+          searchParentBlock = true;
         }
+        this.searchUnknownRoot({slot, root: parentRoot}, searchParentBlock, searchParentEnvelope, peerId);
       }
       preprocessResult = {action: PreprocessAction.PushToQueue};
     }
@@ -443,11 +485,7 @@ export class NetworkProcessor {
               : getDataIndexFromSignedAggregateAndProofSerialized(message.msg.data);
           if (attIndex === 1 && !this.chain.forkChoice.hasPayloadHexUnsafe(root)) {
             // attestation votes that the payload is available but it is not yet known
-            this.searchUnknownEnvelope(
-              {slot, root},
-              BlockInputSource.network_processor,
-              message.propagationSource.toString()
-            );
+            this.searchUnknownRoot({slot, root}, false, true, peerId);
             preprocessResult = {action: PreprocessAction.AwaitEnvelope, root};
           }
           break;
@@ -457,11 +495,7 @@ export class NetworkProcessor {
           const payloadPresent = getPayloadPresentFromPayloadAttestationMessageSerialized(message.msg.data);
           if (payloadPresent && !this.chain.forkChoice.hasPayloadHexUnsafe(root)) {
             // payload attestation votes that the payload is available but it is not yet known
-            this.searchUnknownEnvelope(
-              {slot, root},
-              BlockInputSource.network_processor,
-              message.propagationSource.toString()
-            );
+            this.searchUnknownRoot({slot, root}, false, true, peerId);
             // do not await the envelope, payload attestation processing only requires that the block is known
             // also do not reset preprocessResult, we may already await for the block
           }
@@ -470,11 +504,7 @@ export class NetworkProcessor {
         case GossipType.data_column_sidecar: {
           if (root == null) break;
           if (!this.chain.forkChoice.hasPayloadHexUnsafe(root)) {
-            this.searchUnknownEnvelope(
-              {slot, root},
-              BlockInputSource.network_processor,
-              message.propagationSource.toString()
-            );
+            this.searchUnknownRoot({slot, root}, false, true, peerId);
             // do not await the envelope, we can do gossip validation
             // also do not reset preprocessResult, we may already await for the block
           }
@@ -485,11 +515,7 @@ export class NetworkProcessor {
           // Extract beacon_block_root directly
           const blockRoot = getBeaconBlockRootFromExecutionPayloadEnvelopeSerialized(message.msg.data);
           if (blockRoot && !this.chain.forkChoice.hasBlockHexUnsafe(blockRoot)) {
-            this.searchUnknownBlock(
-              {slot, root: blockRoot},
-              BlockInputSource.network_processor,
-              message.propagationSource.toString()
-            );
+            this.searchUnknownRoot({slot, root: blockRoot}, true, false, peerId);
             // We always want to await the block
             // This allows us to properly forward the payload envelope
             preprocessResult = {action: PreprocessAction.AwaitBlock, root: blockRoot};
@@ -508,21 +534,13 @@ export class NetworkProcessor {
           ) {
             const protoBlock = this.chain.forkChoice.getBlockHexDefaultStatus(parentBlockRoot);
             if (protoBlock === null) {
-              this.searchUnknownBlock(
-                {slot, root: parentBlockRoot},
-                BlockInputSource.network_processor,
-                message.propagationSource.toString()
-              );
+              this.searchUnknownRoot({slot, root: parentBlockRoot}, true, false, peerId);
               preprocessResult = {action: PreprocessAction.AwaitBlock, root: parentBlockRoot};
             } else if (
               protoBlock.executionPayloadBlockHash &&
               protoBlock.executionPayloadBlockHash !== parentBlockHash
             ) {
-              this.searchUnknownEnvelope(
-                {slot, root: parentBlockRoot},
-                BlockInputSource.network_processor,
-                message.propagationSource.toString()
-              );
+              this.searchUnknownRoot({slot, root: parentBlockRoot}, false, true, peerId);
               preprocessResult = {action: PreprocessAction.AwaitEnvelope, root: parentBlockRoot};
             }
           }
@@ -535,42 +553,106 @@ export class NetworkProcessor {
       case PreprocessAction.PushToQueue:
         this.pushPendingGossipsubMessageToQueue(message);
         break;
-      case PreprocessAction.AwaitBlock: {
-        if (this.awaitingBlockMessageCount > MAX_QUEUED_UNKNOWN_BLOCK_GOSSIP_OBJECTS) {
-          // No need to report the dropped job to gossip. It will be eventually pruned from the mcache
-          this.metrics?.awaitingBlockGossipMessages.reject.inc({
-            reason: ReprocessRejectReason.reached_limit,
-            topic: topicType,
-          });
-          return;
-        }
-
-        this.metrics?.awaitingBlockGossipMessages.queue.inc({topic: topicType});
-        const awaitingGossipsubMessages = this.awaitingMessagesByBlockRoot.getOrDefault(preprocessResult.root);
-        awaitingGossipsubMessages.add(message);
-        this.awaitingBlockMessageCount++;
+      case PreprocessAction.AwaitBlock:
+        this.maybeAwaitBlock(preprocessResult.root, topicType, slot, message);
         break;
-      }
-      case PreprocessAction.AwaitEnvelope: {
-        if (this.awaitingPayloadMessageCount > MAX_QUEUED_UNKNOWN_PAYLOAD_GOSSIP_OBJECTS) {
-          this.metrics?.awaitingPayloadGossipMessages.reject.inc({
-            reason: ReprocessRejectReason.reached_limit,
-            topic: topicType,
-          });
-          return;
-        }
-
-        this.metrics?.awaitingPayloadGossipMessages.queue.inc({topic: topicType});
-        const awaitingPayloadGossipsubMessages = this.awaitingMessagesByPayloadBlockRoot.getOrDefault(
-          preprocessResult.root
-        );
-        awaitingPayloadGossipsubMessages.add(message);
-        this.awaitingPayloadMessageCount++;
+      case PreprocessAction.AwaitEnvelope:
+        this.maybeAwaitPayload(preprocessResult.root, topicType, slot, message);
         break;
-      }
     }
   };
 
+  /**
+   * Buffer a gossip message that must wait for an unknown block before it can be validated.
+   *
+   * For DOS protection, the message is ignored (reject metric incremented) when any cap is hit:
+   * - MAX_QUEUED_UNKNOWN_BLOCK_GOSSIP_OBJECTS: global awaiting-block message count
+   * - MAX_BUFFERED_ROOTS_PER_SLOT: distinct roots we buffer messages for, per slot
+   * - MAX_AWAITING_MESSAGES_PER_ROOT[topic]: messages buffered per (root, topic)
+   */
+  private maybeAwaitBlock(root: RootHex, topicType: GossipType, slot: Slot, message: PendingGossipsubMessage): void {
+    const metric = this.metrics?.awaitingBlockGossipMessages;
+    // global message-count cap - cheapest check first
+    if (this.awaitingBlockMessageCount > MAX_QUEUED_UNKNOWN_BLOCK_GOSSIP_OBJECTS) {
+      metric?.reject.inc({reason: ReprocessRejectReason.reached_limit, topic: topicType});
+      return;
+    }
+    // per-(root, topic) message cap: e.g. <= NUMBER_OF_COLUMNS columns per root
+    const perRootCap = MAX_AWAITING_MESSAGES_PER_ROOT[topicType];
+    if (
+      perRootCap !== undefined &&
+      (this.awaitingMessagesByBlockRoot.get(root)?.get(topicType)?.size ?? 0) >= perRootCap
+    ) {
+      metric?.reject.inc({reason: ReprocessRejectReason.reached_topic_limit, topic: topicType});
+      return;
+    }
+    if (!this.tryReserveBufferedRoot(slot, root)) {
+      metric?.reject.inc({reason: ReprocessRejectReason.reached_root_limit, topic: topicType});
+      return;
+    }
+
+    metric?.queue.inc({topic: topicType});
+    this.awaitingMessagesByBlockRoot.getOrDefault(root).getOrDefault(topicType).add(message);
+    this.awaitingBlockMessageCount++;
+  }
+
+  /** Payload counterpart of maybeAwaitBlock */
+  private maybeAwaitPayload(root: RootHex, topicType: GossipType, slot: Slot, message: PendingGossipsubMessage): void {
+    const metric = this.metrics?.awaitingPayloadGossipMessages;
+    if (this.awaitingPayloadMessageCount > MAX_QUEUED_UNKNOWN_PAYLOAD_GOSSIP_OBJECTS) {
+      metric?.reject.inc({reason: ReprocessRejectReason.reached_limit, topic: topicType});
+      return;
+    }
+    const perRootCap = MAX_AWAITING_MESSAGES_PER_ROOT[topicType];
+    if (
+      perRootCap !== undefined &&
+      (this.awaitingMessagesByPayloadBlockRoot.get(root)?.get(topicType)?.size ?? 0) >= perRootCap
+    ) {
+      metric?.reject.inc({reason: ReprocessRejectReason.reached_topic_limit, topic: topicType});
+      return;
+    }
+    if (!this.tryReserveBufferedRoot(slot, root)) {
+      metric?.reject.inc({reason: ReprocessRejectReason.reached_root_limit, topic: topicType});
+      return;
+    }
+
+    metric?.queue.inc({topic: topicType});
+    this.awaitingMessagesByPayloadBlockRoot.getOrDefault(root).getOrDefault(topicType).add(message);
+    this.awaitingPayloadMessageCount++;
+  }
+
+  /**
+   * Cap distinct roots we emit an unknown-root search for, an already-tracked root (dedup) never counts as "too many".
+   */
+  private tooManySearchedRoots(slot: Slot, root: RootHex): boolean {
+    const roots = this.searchedRootsBySlot.get(slot);
+    if (roots === undefined) return false;
+    return !roots.has(root) && roots.size >= MAX_SEARCHED_ROOTS_PER_SLOT;
+  }
+
+  /**
+   * Cap distinct roots we buffer per slot.
+   */
+  tryReserveBufferedRoot(slot: Slot, root: RootHex): boolean {
+    const roots = this.bufferedRootsBySlot.get(slot);
+    if (roots?.has(root)) return true;
+    if ((roots?.size ?? 0) >= MAX_BUFFERED_ROOTS_PER_SLOT) return false;
+    this.bufferedRootsBySlot.getOrDefault(slot).add(root);
+    return true;
+  }
+
+  private searchUnknownRoot(
+    slotRoot: SlotRootHex,
+    searchBlock: boolean,
+    searchEnvelope: boolean,
+    peerId: PeerIdStr
+  ): void {
+    if (!searchBlock && !searchEnvelope) return;
+    if (this.tooManySearchedRoots(slotRoot.slot, slotRoot.root)) return;
+    if (searchBlock) this.searchUnknownBlock(slotRoot, BlockInputSource.network_processor, peerId);
+    if (searchEnvelope) this.searchUnknownEnvelope(slotRoot, BlockInputSource.network_processor, peerId);
+  }
+
   private pushPendingGossipsubMessageToQueue(message: PendingGossipsubMessage): void {
     const topicType = message.topic.type;
     message.queueAddedMs = Date.now();
@@ -585,64 +667,82 @@ export class NetworkProcessor {
   }
 
   private onBlockProcessed = async ({block: rootHex}: {block: string; executionOptimistic: boolean}): Promise<void> => {
-    const waitingGossipsubMessages = this.awaitingMessagesByBlockRoot.get(rootHex);
-    if (!waitingGossipsubMessages || waitingGossipsubMessages.size === 0) {
+    const messagesByTopic = this.awaitingMessagesByBlockRoot.get(rootHex);
+    if (messagesByTopic === undefined) {
+      return;
+    }
+    let total = 0;
+    for (const messages of messagesByTopic.values()) {
+      total += messages.size;
+    }
+    if (total === 0) {
       return;
     }
 
     // Atomically remove from map and update counter before async iteration to
     // prevent double-decrement race with onClockSlot during yield points below
     if (this.awaitingMessagesByBlockRoot.delete(rootHex)) {
-      this.awaitingBlockMessageCount -= waitingGossipsubMessages.size;
+      this.awaitingBlockMessageCount -= total;
     }
 
     const nowSec = Date.now() / 1000;
     let count = 0;
     // TODO: we can group attestations to process in batches but since we have the SeenAttestationDatas
     // cache, it may not be necessary at this time
-    for (const message of waitingGossipsubMessages) {
-      const topicType = message.topic.type;
-      this.metrics?.awaitingBlockGossipMessages.waitSecBeforeResolve.set(
-        {topic: topicType},
-        nowSec - message.seenTimestampSec
-      );
-      this.metrics?.awaitingBlockGossipMessages.resolve.inc({topic: topicType});
-      this.pushPendingGossipsubMessageToQueue(message);
-      count++;
-      // don't want to block the event loop, worse case it'd wait for 16_084 / 1024 * 50ms = 800ms which is not a big deal
-      if (count === MAX_AWAITING_GOSSIP_OBJECTS_PER_TICK) {
-        count = 0;
-        await sleep(AWAITING_GOSSIP_OBJECTS_YIELD_EVERY_MS);
+    for (const messages of messagesByTopic.values()) {
+      for (const message of messages) {
+        const topicType = message.topic.type;
+        this.metrics?.awaitingBlockGossipMessages.waitSecBeforeResolve.set(
+          {topic: topicType},
+          nowSec - message.seenTimestampSec
+        );
+        this.metrics?.awaitingBlockGossipMessages.resolve.inc({topic: topicType});
+        this.pushPendingGossipsubMessageToQueue(message);
+        count++;
+        // don't want to block the event loop, worse case it'd wait for 16_084 / 1024 * 50ms = 800ms which is not a big deal
+        if (count === MAX_AWAITING_GOSSIP_OBJECTS_PER_TICK) {
+          count = 0;
+          await sleep(AWAITING_GOSSIP_OBJECTS_YIELD_EVERY_MS);
+        }
       }
     }
   };
 
   private onPayloadEnvelopeProcessed = async ({blockRoot: rootHex}: {blockRoot: RootHex}): Promise<void> => {
-    const waitingGossipsubMessages = this.awaitingMessagesByPayloadBlockRoot.get(rootHex);
-    if (!waitingGossipsubMessages || waitingGossipsubMessages.size === 0) {
+    const messagesByTopic = this.awaitingMessagesByPayloadBlockRoot.get(rootHex);
+    if (messagesByTopic === undefined) {
+      return;
+    }
+    let total = 0;
+    for (const messages of messagesByTopic.values()) {
+      total += messages.size;
+    }
+    if (total === 0) {
       return;
     }
 
     // Atomically remove from map and update counter before async iteration to
     // prevent double-decrement race with onClockSlot during yield points below
     if (this.awaitingMessagesByPayloadBlockRoot.delete(rootHex)) {
-      this.awaitingPayloadMessageCount -= waitingGossipsubMessages.size;
+      this.awaitingPayloadMessageCount -= total;
     }
 
     const nowSec = Date.now() / 1000;
     let count = 0;
-    for (const message of waitingGossipsubMessages) {
-      const topicType = message.topic.type;
-      this.metrics?.awaitingPayloadGossipMessages.waitSecBeforeResolve.set(
-        {topic: topicType},
-        nowSec - message.seenTimestampSec
-      );
-      this.metrics?.awaitingPayloadGossipMessages.resolve.inc({topic: topicType});
-      this.pushPendingGossipsubMessageToQueue(message);
-      count++;
-      if (count === MAX_AWAITING_GOSSIP_OBJECTS_PER_TICK) {
-        count = 0;
-        await sleep(AWAITING_GOSSIP_OBJECTS_YIELD_EVERY_MS);
+    for (const messages of messagesByTopic.values()) {
+      for (const message of messages) {
+        const topicType = message.topic.type;
+        this.metrics?.awaitingPayloadGossipMessages.waitSecBeforeResolve.set(
+          {topic: topicType},
+          nowSec - message.seenTimestampSec
+        );
+        this.metrics?.awaitingPayloadGossipMessages.resolve.inc({topic: topicType});
+        this.pushPendingGossipsubMessageToQueue(message);
+        count++;
+        if (count === MAX_AWAITING_GOSSIP_OBJECTS_PER_TICK) {
+          count = 0;
+          await sleep(AWAITING_GOSSIP_OBJECTS_YIELD_EVERY_MS);
+        }
       }
     }
   };
@@ -651,12 +751,19 @@ export class NetworkProcessor {
     const nowSec = Date.now() / 1000;
     const minSlot = clockSlot - MAX_UNKNOWN_ROOTS_SLOT_CACHE_SIZE;
 
-    for (const [slot, roots] of this.unknownBlocksBySlot) {
+    for (const [slot, searchedRoots] of this.searchedRootsBySlot) {
       if (slot > minSlot) continue;
-      for (const rootHex of roots.keys()) {
-        const gossipMessages = this.awaitingMessagesByBlockRoot.get(rootHex);
-        if (gossipMessages !== undefined) {
-          for (const message of gossipMessages) {
+
+      // expire messages awaiting an unknown block for these roots. Only roots this slot did a BLOCK search
+      // for (blockPeerIds set) have block waits keyed here; skipping the rest avoids deleting a payload wait
+      // that a newer slot created for the same root (block/envelope searches share searchedRootsBySlot).
+      for (const [rootHex, entry] of searchedRoots) {
+        if (entry.blockPeerIds === undefined) continue;
+        const messagesByTopic = this.awaitingMessagesByBlockRoot.get(rootHex);
+        if (messagesByTopic === undefined) continue;
+        let removed = 0;
+        for (const messages of messagesByTopic.values()) {
+          for (const message of messages) {
             const topicType = message.topic.type;
             this.metrics?.awaitingBlockGossipMessages.reject.inc({
               topic: topicType,
@@ -668,20 +775,22 @@ export class NetworkProcessor {
             );
             // No need to report the dropped job to gossip. It will be eventually pruned from the mcache
           }
-          if (this.awaitingMessagesByBlockRoot.delete(rootHex)) {
-            this.awaitingBlockMessageCount -= gossipMessages.size;
-          }
+          removed += messages.size;
+        }
+        if (this.awaitingMessagesByBlockRoot.delete(rootHex)) {
+          this.awaitingBlockMessageCount -= removed;
         }
       }
-      this.unknownBlocksBySlot.delete(slot);
-    }
 
-    for (const [slot, roots] of this.unknownEnvelopesBySlot) {
-      if (slot > minSlot) continue;
-      for (const rootHex of roots.keys()) {
-        const gossipMessages = this.awaitingMessagesByPayloadBlockRoot.get(rootHex);
-        if (gossipMessages !== undefined) {
-          for (const message of gossipMessages) {
+      // expire messages awaiting an unknown payload envelope for these roots. Symmetric to the block pass:
+      // only roots this slot did an ENVELOPE search for (envelopePeerIds set) have payload waits keyed here.
+      for (const [rootHex, entry] of searchedRoots) {
+        if (entry.envelopePeerIds === undefined) continue;
+        const messagesByTopic = this.awaitingMessagesByPayloadBlockRoot.get(rootHex);
+        if (messagesByTopic === undefined) continue;
+        let removed = 0;
+        for (const messages of messagesByTopic.values()) {
+          for (const message of messages) {
             const topicType = message.topic.type;
             this.metrics?.awaitingPayloadGossipMessages.reject.inc({
               topic: topicType,
@@ -693,12 +802,18 @@ export class NetworkProcessor {
             );
             // No need to report the dropped job to gossip. It will be eventually pruned from the mcache
           }
-          if (this.awaitingMessagesByPayloadBlockRoot.delete(rootHex)) {
-            this.awaitingPayloadMessageCount -= gossipMessages.size;
-          }
+          removed += messages.size;
+        }
+        if (this.awaitingMessagesByPayloadBlockRoot.delete(rootHex)) {
+          this.awaitingPayloadMessageCount -= removed;
         }
       }
-      this.unknownEnvelopesBySlot.delete(slot);
+
+      this.searchedRootsBySlot.delete(slot);
+    }
+
+    for (const slot of this.bufferedRootsBySlot.keys()) {
+      if (slot <= minSlot) this.bufferedRootsBySlot.delete(slot);
     }
   };
 
```

### packages/beacon-node/test/unit/network/processor/networkProcessor.test.ts
```diff
@@ -0,0 +1,308 @@
+import {Mock, beforeEach, describe, expect, it, vi} from "vitest";
+import {config} from "@lodestar/config/default";
+import {ForkName, GENESIS_EPOCH} from "@lodestar/params";
+import {ssz} from "@lodestar/types";
+import {MapDef} from "@lodestar/utils";
+import {ChainEvent, ChainEventEmitter} from "../../../../src/chain/emitter.js";
+import {IBeaconChain} from "../../../../src/chain/interface.js";
+import {IBeaconDb} from "../../../../src/db/interface.js";
+import {NetworkEvent, NetworkEventBus} from "../../../../src/network/events.js";
+import {GossipType} from "../../../../src/network/gossip/interface.js";
+import {
+  MAX_AWAITING_MESSAGES_PER_ROOT,
+  MAX_BUFFERED_ROOTS_PER_SLOT,
+  MAX_SEARCHED_ROOTS_PER_SLOT,
+  NetworkProcessor,
+  NetworkProcessorModules,
+} from "../../../../src/network/processor/index.js";
+import {PendingGossipsubMessage} from "../../../../src/network/processor/types.js";
+import {PeerIdStr} from "../../../../src/util/peerId.js";
+import {ClockStopped} from "../../../mocks/clock.js";
+
+// per-(root, topic) message caps, read from the source so the tests track the real limits
+const MAX_BID_PER_ROOT = MAX_AWAITING_MESSAGES_PER_ROOT[GossipType.execution_payload_bid] as number;
+const MAX_EXECUTION_PAYLOAD_PER_ROOT = MAX_AWAITING_MESSAGES_PER_ROOT[GossipType.execution_payload] as number;
+const MAX_DATA_COLUMN_PER_ROOT = MAX_AWAITING_MESSAGES_PER_ROOT[GossipType.data_column_sidecar] as number;
+
+// When a gossip message points at a block we don't have yet, we hold the message and look the block up.
+// A malicious peer could flood us with messages pointing at blocks that will never arrive, so we put two
+// limits in place: how much we're willing to hold in memory, and how many block lookups we'll start.
+// These tests exercise both limits, and check that a real block is still recovered when an attacker floods.
+describe("NetworkProcessor: handling gossip that points at an unknown block", () => {
+  const clockSlot = 1000;
+  const peerIdStr = "16Uiu2HAmTestGossipPeer" as PeerIdStr;
+
+  let processor: NetworkProcessor;
+  let emitter: ChainEventEmitter;
+  let unknownBlockRootSpy: Mock<(data: unknown) => void>;
+
+  beforeEach(() => {
+    emitter = new ChainEventEmitter();
+    unknownBlockRootSpy = vi.fn();
+    // the unknown-root search (recovery signal to BlockInputSync) is emitted here - our observable surface
+    emitter.on(ChainEvent.unknownBlockRoot, (data) => unknownBlockRootSpy(data));
+
+    const chain = {
+      clock: new ClockStopped(clockSlot),
+      emitter,
+      forkChoice: {
+        hasBlockHexUnsafe: vi.fn().mockReturnValue(false),
+        hasPayloadHexUnsafe: vi.fn().mockReturnValue(false),
+        getBlockHexAndBlockHash: vi.fn().mockReturnValue(undefined),
+        getBlockHexDefaultStatus: vi.fn().mockReturnValue(null),
+      },
+      seenBlock: vi.fn().mockReturnValue(false),
+      seenPayloadEnvelope: vi.fn().mockReturnValue(false),
+    } as unknown as IBeaconChain;
+
+    const modules = {
+      chain,
+      db: null as unknown as IBeaconDb,
+      events: new NetworkEventBus(),
+      config,
+      logger: {debug: vi.fn(), verbose: vi.fn(), info: vi.fn(), warn: vi.fn(), error: vi.fn()},
+      metrics: null,
+      gossipHandlers: {},
+    } as unknown as NetworkProcessorModules;
+
+    processor = new NetworkProcessor(modules, {});
+  });
+
+  function emit(topicType: GossipType, fork: ForkName, data: Uint8Array): void {
+    (processor as unknown as {events: NetworkEventBus}).events.emit(NetworkEvent.pendingGossipsubMessage, {
+      topic: {type: topicType, boundary: {fork, epoch: GENESIS_EPOCH}},
+      msg: {data},
+      msgId: "id",
+      propagationSource: peerIdStr,
+      clientAgent: "",
+      clientVersion: "",
+      seenTimestampSec: 0,
+      startProcessUnixSec: null,
+    } as unknown as PendingGossipsubMessage);
+  }
+
+  /** An aggregate that votes for a different unknown block per `rootByte` (each becomes a distinct unknown block). */
+  function processAggregate(rootByte: number): void {
+    const signedAggregateAndProof = ssz.phase0.SignedAggregateAndProof.defaultValue();
+    signedAggregateAndProof.message.aggregate.data.slot = clockSlot;
+    signedAggregateAndProof.message.aggregate.data.beaconBlockRoot = Buffer.alloc(32, rootByte);
+    const data = ssz.phase0.SignedAggregateAndProof.serialize(signedAggregateAndProof);
+    emit(GossipType.beacon_aggregate_and_proof, ForkName.phase0, data);
+  }
+
+  /** Competing bids from different builders, all for the same unknown block (they pile up under one block). */
+  function processBid(builderIndex: number): void {
+    const signedBid = ssz.gloas.SignedExecutionPayloadBid.defaultValue();
+    signedBid.message.slot = clockSlot;
+    signedBid.message.builderIndex = builderIndex;
+    signedBid.message.parentBlockRoot = Buffer.alloc(32, 0xaa);
+    signedBid.message.parentBlockHash = Buffer.alloc(32, 0xbb);
+    const data = ssz.gloas.SignedExecutionPayloadBid.serialize(signedBid);
+    emit(GossipType.execution_payload_bid, ForkName.gloas, data);
+  }
+
+  /** Data column messages (one per column index), all for the same unknown block. */
+  function processDataColumn(index: number, rootByte = 0xcc): void {
+    const sidecar = ssz.gloas.DataColumnSidecar.defaultValue();
+    sidecar.index = index;
+    sidecar.slot = clockSlot;
+    sidecar.beaconBlockRoot = Buffer.alloc(32, rootByte);
+    const data = ssz.gloas.DataColumnSidecar.serialize(sidecar);
+    emit(GossipType.data_column_sidecar, ForkName.gloas, data);
+  }
+
+  /** An execution payload for an unknown block (there is only ever one payload per block). */
+  function processExecutionPayload(rootByte = 0xdd): void {
+    const signedEnvelope = ssz.gloas.SignedExecutionPayloadEnvelope.defaultValue();
+    signedEnvelope.message.payload.slotNumber = clockSlot;
+    signedEnvelope.message.beaconBlockRoot = Buffer.alloc(32, rootByte);
+    const data = ssz.gloas.SignedExecutionPayloadEnvelope.serialize(signedEnvelope);
+    emit(GossipType.execution_payload, ForkName.gloas, data);
+  }
+
+  function bufferedBlockCount(): number {
+    return (processor as unknown as {awaitingBlockMessageCount: number}).awaitingBlockMessageCount;
+  }
+
+  /** number of distinct block roots we currently hold messages for */
+  function distinctBlockRoots(): number {
+    return (processor as unknown as {awaitingMessagesByBlockRoot: {size: number}}).awaitingMessagesByBlockRoot.size;
+  }
+
+  describe("how many unknown blocks we hold messages for, per slot", () => {
+    it("stops holding messages once too many different blocks are unknown in the same slot", () => {
+      for (let i = 1; i <= MAX_BUFFERED_ROOTS_PER_SLOT + 1; i++) {
+        processAggregate(i);
+      }
+      // we hold messages for at most 5 unknown blocks per slot; messages for the 6th block are dropped,
+      // so a flood of fake blocks can't grow our memory without bound
+      expect(bufferedBlockCount()).toBe(MAX_BUFFERED_ROOTS_PER_SLOT);
+    });
+
+    it("still holds another message for a block we are already waiting on", () => {
+      for (let i = 1; i <= MAX_BUFFERED_ROOTS_PER_SLOT; i++) {
+        processAggregate(i);
+      }
+      expect(bufferedBlockCount()).toBe(MAX_BUFFERED_ROOTS_PER_SLOT);
+      // the limit counts distinct unknown blocks, not messages: a second message for a block we already
+      // wait on is still held, even though we're at the block limit
+      processAggregate(1);
+      expect(bufferedBlockCount()).toBe(MAX_BUFFERED_ROOTS_PER_SLOT + 1);
+    });
+
+    it("keeps looking up a real block even after it stops holding messages for it", () => {
+      for (let i = 1; i <= MAX_BUFFERED_ROOTS_PER_SLOT + 1; i++) {
+        processAggregate(i);
+      }
+      // an attacker can fill the 5 hold slots with fake blocks first; the 6th (real) block is no longer
+      // held, but we still look it up by root, so it can be fetched and the node recovers
+      expect(unknownBlockRootSpy).toHaveBeenCalledTimes(MAX_BUFFERED_ROOTS_PER_SLOT + 1);
+    });
+
+    it("does not let a repeated block sneak past the hold limit (sending each block twice)", () => {
+      // an over-limit block's first message is looked up but not held, which leaves it "tracked". The bug:
+      // a second message for that same block would then be treated as already-held and slip into the buffer,
+      // letting an attacker hold messages for far more than 5 blocks by sending each one twice.
+      const blocks = 10;
+      for (let i = 1; i <= blocks; i++) {
+        processAggregate(i);
+        processAggregate(i); // same block again
+      }
+      // still only 5 distinct blocks are held, no matter how many times each is repeated
+      expect(distinctBlockRoots()).toBe(MAX_BUFFERED_ROOTS_PER_SLOT);
+    });
+  });
+
+  describe("how many messages we hold for a single unknown block", () => {
+    it("holds only a limited number of execution payload bids for one block", () => {
+      for (let i = 0; i < MAX_BID_PER_ROOT + 3; i++) {
+        processBid(i);
+      }
+      // there can be several competing bids for the same block, but we stop holding them after the limit
+      expect(bufferedBlockCount()).toBe(MAX_BID_PER_ROOT);
+    });
+
+    it("holds a limited number of data column messages for one block", () => {
+      for (let i = 0; i < MAX_DATA_COLUMN_PER_ROOT + 3; i++) {
+        processDataColumn(i);
+      }
+      // a block has NUMBER_OF_COLUMNS genuine columns; we allow twice that so malformed front-runners
+      // can't push genuine columns out (a missing column would block import), then stop
+      expect(bufferedBlockCount()).toBe(MAX_DATA_COLUMN_PER_ROOT);
+    });
+
+    it("holds a limited number of execution payloads for one block", () => {
+      for (let i = 0; i < MAX_EXECUTION_PAYLOAD_PER_ROOT + 2; i++) {
+        processExecutionPayload();
+      }
+      // a block has exactly one genuine payload; we keep one extra slot so a malformed front-runner
+      // doesn't push the genuine payload out, then drop further messages
+      expect(bufferedBlockCount()).toBe(MAX_EXECUTION_PAYLOAD_PER_ROOT);
+    });
+  });
+
+  describe("how many unknown blocks we look up by root, per slot", () => {
+    it("stops looking up new blocks once too many are unknown in the same slot", () => {
+      for (let i = 1; i <= MAX_SEARCHED_ROOTS_PER_SLOT + 1; i++) {
+        processAggregate(i);
+      }
+      // the lookup limit is higher than the hold limit (so real blocks past the hold limit still recover),
+      // but it's still bounded, so a flood can't make us start unlimited lookups
+      expect(unknownBlockRootSpy).toHaveBeenCalledTimes(MAX_SEARCHED_ROOTS_PER_SLOT);
+    });
+
+    it("looks up a block only once, no matter how many messages point at it", () => {
+      processAggregate(1);
+      processAggregate(1); // another message for the same unknown block
+      expect(unknownBlockRootSpy).toHaveBeenCalledTimes(1);
+      // the repeated message triggers no extra lookup, but is still held
+      expect(bufferedBlockCount()).toBe(2);
+    });
+  });
+
+  describe("expiring old unknown blocks", () => {
+    type Entry = {blockPeerIds?: Set<string>; envelopePeerIds?: Set<string>};
+    type Internals = {
+      searchedRootsBySlot: MapDef<number, MapDef<string, Entry>>;
+      awaitingMessagesByBlockRoot: MapDef<string, MapDef<GossipType, Set<PendingGossipsubMessage>>>;
+      awaitingMessagesByPayloadBlockRoot: MapDef<string, MapDef<GossipType, Set<PendingGossipsubMessage>>>;
+      awaitingBlockMessageCount: number;
+      awaitingPayloadMessageCount: number;
+      onClockSlot: (slot: number) => void;
+    };
+
+    it("expiring a block wait for one block does not drop a newer payload wait for the same block", () => {
+      // block lookups and payload lookups for a block are tracked together per slot. A block may be looked
+      // up at one slot and, later (after the block arrives), its payload waited on from a newer slot. Expiring
+      // the old slot must not also drop the newer payload wait just because they share the same block.
+      const p = processor as unknown as Internals;
+      const root = `0x${"ab".repeat(32)}`;
+      const oldSlot = clockSlot - 4; // expires this tick (<= clockSlot - MAX_UNKNOWN_ROOTS_SLOT_CACHE_SIZE)
+      const newSlot = clockSlot; //     must survive
+      const message = (): PendingGossipsubMessage =>
+        ({
+          topic: {type: GossipType.beacon_aggregate_and_proof},
+          seenTimestampSec: 0,
+        }) as unknown as PendingGossipsubMessage;
+
+      // old slot: a block lookup for `root`, with a message waiting for that block
+      p.searchedRootsBySlot.getOrDefault(oldSlot).getOrDefault(root).blockPeerIds = new Set();
+      p.awaitingMessagesByBlockRoot
+        .getOrDefault(root)
+        .getOrDefault(GossipType.beacon_aggregate_and_proof)
+        .add(message());
+      p.awaitingBlockMessageCount++;
+
+      // newer slot: a payload lookup for the SAME `root`, with a message waiting for that payload
+      p.searchedRootsBySlot.getOrDefault(newSlot).getOrDefault(root).envelopePeerIds = new Set();
+      p.awaitingMessagesByPayloadBlockRoot
+        .getOrDefault(root)
+        .getOrDefault(GossipType.beacon_aggregate_and_proof)
+        .add(message());
+      p.awaitingPayloadMessageCount++;
+
+      p.onClockSlot(clockSlot);
+
+      // the old block wait is expired
+      expect(p.awaitingMessagesByBlockRoot.has(root)).toBe(false);
+      // the newer payload wait survives - it belongs to a slot that hasn't expired
+      expect(p.awaitingMessagesByPayloadBlockRoot.has(root)).toBe(true);
+    });
+  });
+
+  describe("tryReserveBufferedRoot", () => {
+    function reserve(slot: number, root: string): boolean {
+      return (
+        processor as unknown as {tryReserveBufferedRoot: (slot: number, root: string) => boolean}
+      ).tryReserveBufferedRoot(slot, root);
+    }
+
+    it("reserves up to MAX_BUFFERED_ROOTS_PER_SLOT distinct roots per slot, then refuses new ones", () => {
+      for (let i = 0; i < MAX_BUFFERED_ROOTS_PER_SLOT; i++) {
+        expect(reserve(clockSlot, `0x0${i}`)).toBe(true);
+      }
+      // budget full -> a new root is refused
+      expect(reserve(clockSlot, "0xnew")).toBe(false);
+    });
+
+    it("is idempotent: an already-reserved root stays allowed and never consumes a second slot", () => {
+      for (let i = 0; i < MAX_BUFFERED_ROOTS_PER_SLOT; i++) {
+        expect(reserve(clockSlot, `0x0${i}`)).toBe(true);
+      }
+      // re-reserving existing roots any number of times is still allowed and doesn't overflow the budget
+      expect(reserve(clockSlot, "0x00")).toBe(true);
+      expect(reserve(clockSlot, "0x00")).toBe(true);
+      // ...and a genuinely new root is still refused (the repeats didn't free or take extra slots)
+      expect(reserve(clockSlot, "0xnew")).toBe(false);
+    });
+
+    it("budgets each slot independently", () => {
+      for (let i = 0; i < MAX_BUFFERED_ROOTS_PER_SLOT; i++) {
+        expect(reserve(clockSlot, `0x0${i}`)).toBe(true);
+      }
+      expect(reserve(clockSlot, "0xover")).toBe(false);
+      // a different slot has its own budget
+      expect(reserve(clockSlot + 1, "0xover")).toBe(true);
+    });
+  });
+});
```
