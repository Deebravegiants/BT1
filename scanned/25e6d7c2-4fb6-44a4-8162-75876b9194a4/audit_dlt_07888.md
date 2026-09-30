# [?] DOS protection based on message slot (#5394)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ChainSafe/lodestar
Published: 2023-04-21
Source: https://github.com/ChainSafe/lodestar/commit/e746f9cae45a8b7bb0f51e1400c985c64b189c21
Type: security-commit

## Details
DOS protection based on message slot (#5394)

* Add GossipErrorCode.PAST_SLOT

* Add getSlotFromSignedBeaconBlockSerialized() util

* DOS protection: avoid processing messages that are too old

## Patch
### packages/beacon-node/src/chain/errors/gossipValidation.ts
```diff
@@ -5,7 +5,10 @@ export enum GossipAction {
   REJECT = "REJECT",
 }
 
-export const INVALID_SERIALIZED_BYTES_ERROR_CODE = "GOSSIP_ERROR_INVALID_SERIALIZED_BYTES";
+export enum GossipErrorCode {
+  INVALID_SERIALIZED_BYTES_ERROR_CODE = "GOSSIP_ERROR_INVALID_SERIALIZED_BYTES",
+  PAST_SLOT = "GOSSIP_ERROR_PAST_SLOT",
+}
 
 export class GossipActionError<T extends {code: string}> extends LodestarError<T> {
   action: GossipAction;
```

### packages/beacon-node/src/metrics/metrics/lodestar.ts
```diff
@@ -276,11 +276,6 @@ export function createLodestarMetrics(
       help: "Current count of jobs being run on network processor for topic",
       labelNames: ["topic"],
     }),
-    gossipValidationErrorTooManySkippedSlots: register.gauge<"topic">({
-      name: "lodestar_gossip_validation_error_too_many_skipped_slots_total",
-      help: "Count of total gossip validation errors due to too many skipped slots",
-      labelNames: ["topic"],
-    }),
 
     networkProcessor: {
       executeWorkCalls: register.gauge({
```

### packages/beacon-node/src/network/gossip/topic.ts
```diff
@@ -8,11 +8,7 @@ import {
   isForkLightClient,
 } from "@lodestar/params";
 
-import {
-  GossipAction,
-  GossipActionError,
-  INVALID_SERIALIZED_BYTES_ERROR_CODE,
-} from "../../chain/errors/gossipValidation.js";
+import {GossipAction, GossipActionError, GossipErrorCode} from "../../chain/errors/gossipValidation.js";
 import {GossipEncoding, GossipTopic, GossipType, GossipTopicTypeMap, SSZTypeOfGossipTopic} from "./interface.js";
 import {DEFAULT_ENCODING} from "./constants.js";
 
@@ -123,7 +119,7 @@ export function sszDeserialize<T extends GossipTopic>(topic: T, serializedData:
   try {
     return sszType.deserialize(serializedData) as SSZTypeOfGossipTopic<T>;
   } catch (e) {
-    throw new GossipActionError(GossipAction.REJECT, {code: INVALID_SERIALIZED_BYTES_ERROR_CODE});
+    throw new GossipActionError(GossipAction.REJECT, {code: GossipErrorCode.INVALID_SERIALIZED_BYTES_ERROR_CODE});
   }
 }
 
@@ -134,7 +130,7 @@ export function sszDeserializeAttestation(serializedData: Uint8Array): phase0.At
   try {
     return ssz.phase0.Attestation.deserialize(serializedData);
   } catch (e) {
-    throw new GossipActionError(GossipAction.REJECT, {code: INVALID_SERIALIZED_BYTES_ERROR_CODE});
+    throw new GossipActionError(GossipAction.REJECT, {code: GossipErrorCode.INVALID_SERIALIZED_BYTES_ERROR_CODE});
   }
 }
 
```

### packages/beacon-node/src/network/processor/extractSlotRootFns.ts
```diff
@@ -1,9 +1,11 @@
-import {SlotRootHex} from "@lodestar/types";
+import {SlotOptionalRoot, SlotRootHex} from "@lodestar/types";
 import {
   getBlockRootFromAttestationSerialized,
   getBlockRootFromSignedAggregateAndProofSerialized,
   getSlotFromAttestationSerialized,
   getSlotFromSignedAggregateAndProofSerialized,
+  getSlotFromSignedBeaconBlockAndBlobsSidecarSerialized,
+  getSlotFromSignedBeaconBlockSerialized,
 } from "../../util/sszBytes.js";
 import {GossipType} from "../gossip/index.js";
 import {ExtractSlotRootFns} from "./types.js";
@@ -32,5 +34,21 @@ export function createExtractBlockSlotRootFns(): ExtractSlotRootFns {
       }
       return {slot, root};
     },
+    [GossipType.beacon_block]: (data: Uint8Array): SlotOptionalRoot | null => {
+      const slot = getSlotFromSignedBeaconBlockSerialized(data);
+
+      if (slot === null) {
+        return null;
+      }
+      return {slot};
+    },
+    [GossipType.beacon_block_and_blobs_sidecar]: (data: Uint8Array): SlotOptionalRoot | null => {
+      const slot = getSlotFromSignedBeaconBlockAndBlobsSidecarSerialized(data);
+
+      if (slot === null) {
+        return null;
+      }
+      return {slot};
+    },
   };
 }
```

### packages/beacon-node/src/network/processor/gossipHandlers.ts
```diff
@@ -203,13 +203,8 @@ export function getGossipHandlers(modules: ValidatorFnsModules, options: GossipH
       try {
         validationResult = await validateGossipAggregateAndProof(chain, signedAggregateAndProof, false, serializedData);
       } catch (e) {
-        if (e instanceof AttestationError) {
-          if (e.action === GossipAction.REJECT) {
-            chain.persistInvalidSszValue(ssz.phase0.SignedAggregateAndProof, signedAggregateAndProof, "gossip_reject");
-          }
-          if (e.type.code === AttestationErrorCode.TOO_MANY_SKIPPED_SLOTS) {
-            metrics?.gossipValidationErrorTooManySkippedSlots.inc({topic: topic.type});
-          }
+        if (e instanceof AttestationError && e.action === GossipAction.REJECT) {
+          chain.persistInvalidSszValue(ssz.phase0.SignedAggregateAndProof, signedAggregateAndProof, "gossip_reject");
         }
         throw e;
       }
@@ -239,7 +234,7 @@ export function getGossipHandlers(modules: ValidatorFnsModules, options: GossipH
       }
     },
 
-    [GossipType.beacon_attestation]: async ({serializedData, msgSlot}, {type, subnet}, _peer, seenTimestampSec) => {
+    [GossipType.beacon_attestation]: async ({serializedData, msgSlot}, {subnet}, _peer, seenTimestampSec) => {
       if (msgSlot === undefined) {
         throw Error("msgSlot is undefined for beacon_attestation topic");
       }
@@ -252,13 +247,8 @@ export function getGossipHandlers(modules: ValidatorFnsModules, options: GossipH
           subnet
         );
       } catch (e) {
-        if (e instanceof AttestationError) {
-          if (e.action === GossipAction.REJECT) {
-            chain.persistInvalidSszBytes(ssz.phase0.Attestation.typeName, serializedData, "gossip_reject");
-          }
-          if (e.type.code === AttestationErrorCode.TOO_MANY_SKIPPED_SLOTS) {
-            metrics?.gossipValidationErrorTooManySkippedSlots.inc({topic: type});
-          }
+        if (e instanceof AttestationError && e.action === GossipAction.REJECT) {
+          chain.persistInvalidSszBytes(ssz.phase0.Attestation.typeName, serializedData, "gossip_reject");
         }
         throw e;
       }
```

### packages/beacon-node/src/network/processor/index.ts
```diff
@@ -6,6 +6,7 @@ import {Metrics} from "../../metrics/metrics.js";
 import {NetworkEvent, NetworkEventBus} from "../events.js";
 import {GossipType} from "../gossip/interface.js";
 import {ChainEvent} from "../../chain/emitter.js";
+import {GossipErrorCode} from "../../chain/errors/gossipValidation.js";
 import {createGossipQueues} from "./gossipQueues.js";
 import {NetworkWorker, NetworkWorkerModules} from "./worker.js";
 import {PendingGossipsubMessage} from "./types.js";
@@ -24,6 +25,14 @@ export type NetworkProcessorOpts = GossipHandlerOpts & {
   maxGossipTopicConcurrency?: number;
 };
 
+/**
+ * This is respective to gossipsub seenTTL (which is 550 * 0.7 = 385s), also it's respective
+ * to beacon_attestation ATTESTATION_PROPAGATION_SLOT_RANGE (32 slots).
+ * If message slots are withint this window, it'll likely to be filtered by gossipsub seenCache.
+ * This is mainly for DOS protection, see https://github.com/ChainSafe/lodestar/issues/5393
+ */
+const EARLIEST_PERMISSABLE_SLOT_DISTANCE = 32;
+
 type WorkOpts = {
   bypassQueue?: boolean;
 };
@@ -171,10 +180,15 @@ export class NetworkProcessor {
       // if slotRoot is null, it means the msg.data is invalid
       // in that case message will be rejected when deserializing data in later phase (gossipValidatorFn)
       if (slotRoot) {
-        // msgSlot is only available for beacon_attestation and aggregate_and_proof
+        // DOS protection: avoid processing messages that are too old
         const {slot, root} = slotRoot;
+        if (slot < this.chain.clock.currentSlot - EARLIEST_PERMISSABLE_SLOT_DISTANCE) {
+          // TODO: Should report the dropped job to gossip? It will be eventually pruned from the mcache
+          this.metrics?.gossipValidationError.inc({topic: message.topic.type, error: GossipErrorCode.PAST_SLOT});
+          return;
+        }
         message.msgSlot = slot;
-        if (!this.chain.forkChoice.hasBlockHex(root)) {
+        if (root && !this.chain.forkChoice.hasBlockHex(root)) {
           if (this.unknownBlockGossipsubMessagesCount > MAX_QUEUED_UNKNOWN_BLOCK_GOSSIP_OBJECTS) {
             // TODO: Should report the dropped job to gossip? It will be eventually pruned from the mcache
             this.metrics?.reprocessGossipAttestations.reject.inc({reason: ReprocessRejectReason.reached_limit});
```

### packages/beacon-node/src/network/processor/types.ts
```diff
@@ -1,6 +1,6 @@
 import {PeerId} from "@libp2p/interface-peer-id";
 import {Message} from "@libp2p/interface-pubsub";
-import {Slot, SlotRootHex} from "@lodestar/types";
+import {Slot, SlotOptionalRoot} from "@lodestar/types";
 import {GossipTopic, GossipType} from "../gossip/index.js";
 
 export type GossipAttestationsWork = {
@@ -20,5 +20,5 @@ export type PendingGossipsubMessage = {
 };
 
 export type ExtractSlotRootFns = {
-  [K in GossipType]?: (data: Uint8Array) => SlotRootHex | null;
+  [K in GossipType]?: (data: Uint8Array) => SlotOptionalRoot | null;
 };
```

### packages/beacon-node/src/network/reqresp/handlers/beaconBlockAndBlobsSidecarByRoot.ts
```diff
@@ -3,7 +3,7 @@ import {deneb} from "@lodestar/types";
 import {toHex} from "@lodestar/utils";
 import {IBeaconChain} from "../../../chain/index.js";
 import {IBeaconDb} from "../../../db/index.js";
-import {getSlotFromBytes} from "../../../util/multifork.js";
+import {getSlotFromSignedBeaconBlockSerialized} from "../../../util/sszBytes.js";
 
 export async function* onBeaconBlockAndBlobsSidecarByRoot(
   requestBody: deneb.BeaconBlockAndBlobsSidecarByRootRequest,
@@ -35,12 +35,17 @@ export async function* onBeaconBlockAndBlobsSidecarByRoot(
       throw Error(`Inconsistent state, blobsSidecar known to fork-choice not in db ${blockRootHex}`);
     }
 
+    const forkSlot = getSlotFromSignedBeaconBlockSerialized(blockBytes);
+    if (forkSlot === null) {
+      throw Error(`Invalid block bytes for block ${blockRootHex}`);
+    }
+
     yield {
       type: EncodedPayloadType.bytes,
       bytes: signedBeaconBlockAndBlobsSidecarFromBytes(blockBytes, blobsSidecarBytes),
       contextBytes: {
         type: ContextBytesType.ForkDigest,
-        forkSlot: getSlotFromBytes(blockBytes),
+        forkSlot,
       },
     };
   }
```

### packages/beacon-node/src/network/reqresp/handlers/beaconBlocksByRoot.ts
```diff
@@ -1,8 +1,9 @@
+import {toHexString} from "@chainsafe/ssz";
 import {EncodedPayload, EncodedPayloadType, ContextBytesType} from "@lodestar/reqresp";
 import {allForks, phase0, Slot} from "@lodestar/types";
 import {IBeaconChain} from "../../../chain/index.js";
 import {IBeaconDb} from "../../../db/index.js";
-import {getSlotFromBytes} from "../../../util/multifork.js";
+import {getSlotFromSignedBeaconBlockSerialized} from "../../../util/sszBytes.js";
 
 export async function* onBeaconBlocksByRoot(
   requestBody: phase0.BeaconBlocksByRootRequest,
@@ -27,13 +28,22 @@ export async function* onBeaconBlocksByRoot(
         blockBytes = blockEntry.value;
       }
     }
+
     if (blockBytes) {
+      if (slot === undefined) {
+        const slotFromBytes = getSlotFromSignedBeaconBlockSerialized(blockBytes);
+        if (slotFromBytes === null) {
+          throw Error(`Invalid block bytes for block root ${toHexString(root)}`);
+        }
+        slot = slotFromBytes;
+      }
+
       yield {
         type: EncodedPayloadType.bytes,
         bytes: blockBytes,
         contextBytes: {
           type: ContextBytesType.ForkDigest,
-          forkSlot: slot ?? getSlotFromBytes(blockBytes),
+          forkSlot: slot,
         },
       };
     }
```

### packages/beacon-node/src/util/multifork.ts
```diff
@@ -1,27 +1,13 @@
 import {ChainForkConfig} from "@lodestar/config";
-import {allForks, Slot} from "@lodestar/types";
+import {allForks} from "@lodestar/types";
 import {bytesToInt} from "@lodestar/utils";
+import {getSlotFromSignedBeaconBlockSerialized} from "./sszBytes.js";
 
 /**
  * Slot	uint64
  */
 const SLOT_BYTE_COUNT = 8;
-/**
- * 4 + 96 = 100
- * ```
- * class SignedBeaconBlock(Container):
- *   message: BeaconBlock [offset - 4 bytes]
- *   signature: BLSSignature [fixed - 96 bytes]
- *
- * class BeaconBlock(Container):
- *   slot: Slot [fixed - 8 bytes]
- *   proposer_index: ValidatorIndex
- *   parent_root: Root
- *   state_root: Root
- *   body: BeaconBlockBody
- * ```
- */
-const SLOT_BYTES_POSITION_IN_BLOCK = 100;
+
 /**
  * 8 + 32 = 40
  * ```
@@ -38,12 +24,12 @@ export function getSignedBlockTypeFromBytes(
   config: ChainForkConfig,
   bytes: Buffer | Uint8Array
 ): allForks.AllForksSSZTypes["SignedBeaconBlock"] {
-  const slot = getSlotFromBytes(bytes);
-  return config.getForkTypes(slot).SignedBeaconBlock;
-}
+  const slot = getSlotFromSignedBeaconBlockSerialized(bytes);
+  if (slot === null) {
+    throw Error("getSignedBlockTypeFromBytes: invalid bytes");
+  }
 
-export function getSlotFromBytes(bytes: Buffer | Uint8Array): Slot {
-  return bytesToInt(bytes.subarray(SLOT_BYTES_POSITION_IN_BLOCK, SLOT_BYTES_POSITION_IN_BLOCK + SLOT_BYTE_COUNT));
+  return config.getForkTypes(slot).SignedBeaconBlock;
 }
 
 export function getStateTypeFromBytes(
```

### packages/beacon-node/src/util/sszBytes.ts
```diff
@@ -16,15 +16,6 @@ export type AttDataBase64 = string;
 //   beacon_block_root: Root   - data 32
 //   source: Checkpoint        - data 40
 //   target: Checkpoint        - data 40
-//
-// class SignedAggregateAndProof(Container):
-//    message: AggregateAndProof - offset 4
-//    signature: BLSSignature    - data 96
-
-// class AggregateAndProof(Container)
-//    aggregatorIndex: ValidatorIndex - data 8
-//    aggregate: Attestation          - offset 4
-//    selectionProof: BLSSignature    - data 96
 
 const VARIABLE_FIELD_OFFSET = 4;
 const ATTESTATION_BEACON_BLOCK_ROOT_OFFSET = VARIABLE_FIELD_OFFSET + 8 + 8;
@@ -104,6 +95,16 @@ export function getSignatureFromAttestationSerialized(data: Uint8Array): BLSSign
   );
 }
 
+//
+// class SignedAggregateAndProof(Container):
+//    message: AggregateAndProof - offset 4
+//    signature: BLSSignature    - data 96
+
+// class AggregateAndProof(Container)
+//    aggregatorIndex: ValidatorIndex - data 8
+//    aggregate: Attestation          - offset 4
+//    selectionProof: BLSSignature    - data 96
+
 const AGGREGATE_AND_PROOF_OFFSET = 4 + 96;
 const AGGREGATE_OFFSET = AGGREGATE_AND_PROOF_OFFSET + 8 + 4 + 96;
 const SIGNED_AGGREGATE_AND_PROOF_SLOT_OFFSET = AGGREGATE_OFFSET + VARIABLE_FIELD_OFFSET;
@@ -153,6 +154,57 @@ export function getAttDataBase64FromSignedAggregateAndProofSerialized(data: Uint
   ).toString("base64");
 }
 
+/**
+ * 4 + 96 = 100
+ * ```
+ * class SignedBeaconBlock(Container):
+ *   message: BeaconBlock [offset - 4 bytes]
+ *   signature: BLSSignature [fixed - 96 bytes]
+ *
+ * class BeaconBlock(Container):
+ *   slot: Slot [fixed - 8 bytes]
+ *   proposer_index: ValidatorIndex
+ *   parent_root: Root
+ *   state_root: Root
+ *   body: BeaconBlockBody
+ * ```
+ */
+const SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK = VARIABLE_FIELD_OFFSET + SIGNATURE_SIZE;
+
+export function getSlotFromSignedBeaconBlockSerialized(data: Uint8Array): Slot | null {
+  if (data.length < SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK + SLOT_SIZE) {
+    return null;
+  }
+
+  return getSlotFromOffset(data, SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK);
+}
+
+/**
+ * 4 + 4 + SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK = 4 + 4 + (4 + 96) = 108
+ * class SignedBeaconBlockAndBlobsSidecar(Container):
+ *  beaconBlock: SignedBeaconBlock [offset - 4 bytes]
+ *  blobsSidecar: BlobsSidecar,
+ */
+
+/**
+ * Variable size.
+ * class BlobsSidecar(Container):
+ *   beaconBlockRoot: Root,
+ *   beaconBlockSlot: Slot,
+ *   blobs: Blobs,
+ *   kzgAggregatedProof: KZGProof,
+ */
+const SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK_AND_BLOBS_SIDECAR =
+  VARIABLE_FIELD_OFFSET + VARIABLE_FIELD_OFFSET + SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK;
+
+export function getSlotFromSignedBeaconBlockAndBlobsSidecarSerialized(data: Uint8Array): Slot | null {
+  if (data.length < SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK_AND_BLOBS_SIDECAR + SLOT_SIZE) {
+    return null;
+  }
+
+  return getSlotFromOffset(data, SLOT_BYTES_POSITION_IN_SIGNED_BEACON_BLOCK_AND_BLOBS_SIDECAR);
+}
+
 function getSlotFromOffset(data: Uint8Array, offset: number): Slot {
   // TODO: Optimize
   const dv = new DataView(data.buffer, data.byteOffset, data.byteLength);
```

### packages/beacon-node/test/unit/chain/validation/attestation.test.ts
```diff
@@ -3,7 +3,7 @@ import {BitArray} from "@chainsafe/ssz";
 import {processSlots} from "@lodestar/state-transition";
 import {ssz} from "@lodestar/types";
 import {IBeaconChain} from "../../../../src/chain/index.js";
-import {AttestationErrorCode, INVALID_SERIALIZED_BYTES_ERROR_CODE} from "../../../../src/chain/errors/index.js";
+import {AttestationErrorCode, GossipErrorCode} from "../../../../src/chain/errors/index.js";
 import {AttestationOrBytes, validateGossipAttestation} from "../../../../src/chain/validation/index.js";
 import {expectRejectedWithLodestarError} from "../../../utils/errors.js";
 import {generateTestCachedBeaconStateOnlyValidators} from "../../../../../state-transition/test/perf/util.js";
@@ -47,7 +47,7 @@ describe("chain / validation / attestation", () => {
       chain,
       {attestation: null, serializedData: Buffer.alloc(0), attSlot: 0},
       subnet,
-      INVALID_SERIALIZED_BYTES_ERROR_CODE
+      GossipErrorCode.INVALID_SERIALIZED_BYTES_ERROR_CODE
     );
   });
 
```
