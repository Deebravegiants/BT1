# [?] feat: protect epoch-proof fees against an unsound verifier

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-06-19
Source: https://github.com/AztecProtocol/aztec-packages/commit/8b1ea21eda573bcdb1bc5562ef36b164e8dd8a6e
Type: security-commit

## Details
feat: protect epoch-proof fees against an unsound verifier

Port of #24186 to the v5 release line.

Bind per-checkpoint fee recipient/value to the committee-attested checkpoint
header instead of prover-supplied calldata, so reward distribution and the epoch
proof's fee-region public inputs are derived from headers verified on L1 and no
longer depend on a sound verifier.

- L1: add ProposedHeader.accumulatedFees (hashed in ProposedHeaderLib); replace
  SubmitEpochRootProofArgs.fees[] with headers[]; submitEpochRootProof rehashes
  each supplied header against the stored hash; RewardLib and
  getEpochProofPublicInputs read recipient/value from the verified headers.
- Circuits: add accumulated_fees to CheckpointHeader (hash + serialize) and set
  it in the checkpoint-root composer; bump CHECKPOINT_HEADER_LENGTH.
- Off-chain: thread checkpoint headers from the prover node's epoch session
  through the proof-publishing service to the L1 submit call; archiver, sequencer
  and stdlib carry the new field.
- PXE: bump PXE_DATA_SCHEMA_VERSION (8 -> 9) for the checkpoint serialization
  change and regenerate the storage compatibility snapshots.

## Patch
### l1-contracts/src/core/Rollup.sol
```diff
@@ -292,16 +292,15 @@ contract Rollup is IStaking, IValidatorSelection, IRollup, RollupCore {
    * @param  _start - The start of the epoch (inclusive)
    * @param  _end - The end of the epoch (inclusive)
    * @param  _args - Array of public inputs to the proof (previousArchive, endArchive, endTimestamp, outHash, proverId)
-   * @param  _fees - Array of recipient-value pairs with fees to be distributed for the epoch
    */
   function getEpochProofPublicInputs(
     uint256 _start,
     uint256 _end,
     PublicInputArgs calldata _args,
-    bytes32[] calldata _fees,
+    ProposedHeader[] calldata _headers,
     bytes calldata _blobPublicInputs
   ) external view override(IRollup) returns (bytes32[] memory) {
-    return RollupOperationsExtLib.getEpochProofPublicInputs(_start, _end, _args, _fees, _blobPublicInputs);
+    return RollupOperationsExtLib.getEpochProofPublicInputs(_start, _end, _args, _headers, _blobPublicInputs);
   }
 
   /**
```

### l1-contracts/src/core/interfaces/IRollup.sol
```diff
@@ -34,7 +34,7 @@ struct SubmitEpochRootProofArgs {
   uint256 start; // inclusive
   uint256 end; // inclusive
   PublicInputArgs args;
-  bytes32[] fees;
+  ProposedHeader[] headers; // Must match what was proposed by the committee
   CommitteeAttestations attestations; // attestations for the last checkpoint in epoch
   bytes blobInputs;
   bytes proof;
@@ -184,7 +184,7 @@ interface IRollup is IRollupCore, IHaveVersion {
     uint256 _start,
     uint256 _end,
     PublicInputArgs calldata _args,
-    bytes32[] calldata _fees,
+    ProposedHeader[] calldata _headers,
     bytes calldata _blobPublicInputs
   ) external view returns (bytes32[] memory);
 
```

### l1-contracts/src/core/libraries/Errors.sol
```diff
@@ -54,6 +54,8 @@ library Errors {
   error Rollup__InsufficientBondAmount(uint256 minimum, uint256 provided); // 0xa165f276
   error Rollup__InsufficientFundsInEscrow(uint256 required, uint256 available); // 0xa165f276
   error Rollup__InvalidArchive(bytes32 expected, bytes32 actual); // 0xb682a40e
+  error Rollup__InvalidCheckpointHeader(bytes32 expected, bytes32 actual);
+  error Rollup__InvalidCheckpointHeaderCount(uint256 expected, uint256 actual);
   error Rollup__InvalidCheckpointNumber(uint256 expected, uint256 actual); // 0xd1ba9bfa
   error Rollup__InvalidInHash(bytes32 expected, bytes32 actual); // 0xcd6f4233
   error Rollup__InvalidOutHash(bytes32 expected, bytes32 actual); // 0x8eb39062
```

### l1-contracts/src/core/libraries/rollup/EpochProofLib.sol
```diff
@@ -11,6 +11,7 @@ import {ChainTipsLib, CompressedChainTips} from "@aztec/core/libraries/compresse
 import {Constants} from "@aztec/core/libraries/ConstantsGen.sol";
 import {Errors} from "@aztec/core/libraries/Errors.sol";
 import {AttestationLib, CommitteeAttestations} from "@aztec/core/libraries/rollup/AttestationLib.sol";
+import {ProposedHeader, ProposedHeaderLib} from "@aztec/core/libraries/rollup/ProposedHeaderLib.sol";
 import {RewardLib} from "@aztec/core/libraries/rollup/RewardLib.sol";
 import {STFLib} from "@aztec/core/libraries/rollup/STFLib.sol";
 import {ValidatorSelectionLib} from "@aztec/core/libraries/rollup/ValidatorSelectionLib.sol";
@@ -96,7 +97,7 @@ library EpochProofLib {
    *              - start: First checkpoint number in the epoch (inclusive)
    *              - end: Last checkpoint number in the epoch (inclusive)
    *              - args: Public inputs (previousArchive, endArchive, endTimestamp, proverId)
-   *              - fees: Fee distribution array (recipient-value pairs)
+   *              - headers: Proposed headers for each checkpoint, supplying the fee recipient and value
    *              - attestations: Committee attestations for the last checkpoint in the epoch
    *              - blobInputs: Batched blob data for EIP-4844 point evaluation precompile
    *              - proof: The validity proof bytes for the root rollup circuit
@@ -108,6 +109,8 @@ library EpochProofLib {
 
     Epoch endEpoch = assertAcceptable(_args.start, _args.end);
 
+    verifyHeaders(_args.start, _args.end, _args.headers);
+
     // Verify attestations for the last checkpoint in the epoch
     // -> This serves as training wheels for the public part of the system (proving systems used in public and AVM)
     // ensuring committee agreement on the epoch's validity alongside the cryptographic proof verification below.
@@ -150,14 +153,14 @@ library EpochProofLib {
    * @param  _start - The start of the epoch (inclusive)
    * @param  _end - The end of the epoch (inclusive)
    * @param  _args - Array of public inputs to the proof (previousArchive, endArchive, endTimestamp, outHash, proverId)
-   * @param  _fees - Array of recipient-value pairs with fees to be distributed for the epoch
+   * @param  _headers - The proposed checkpoint headers supplying the fee recipient and value for each checkpoint
    * @param _blobPublicInputs- The blob public inputs for the proof
    */
   function getEpochProofPublicInputs(
     uint256 _start,
     uint256 _end,
     PublicInputArgs calldata _args,
-    bytes32[] calldata _fees,
+    ProposedHeader[] calldata _headers,
     bytes calldata _blobPublicInputs
   ) internal view returns (bytes32[] memory) {
     RollupStore storage rollupStore = STFLib.getStorage();
@@ -215,12 +218,13 @@ library EpochProofLib {
 
     uint256 offset = 3 + Constants.MAX_CHECKPOINTS_PER_EPOCH;
 
-    uint256 feesLength = Constants.MAX_CHECKPOINTS_PER_EPOCH * 2;
-    // fees[2n to 2n + 1]: a fee element, which contains of a recipient and a value
-    for (uint256 i = 0; i < feesLength; i++) {
-      publicInputs[offset + i] = _fees[i];
+    // Taking recipient/value from the checkpoint headers rather than the prover
+    // as defense in depth. Slots past numCheckpoints stay zero.
+    for (uint256 i = 0; i < numCheckpoints; i++) {
+      publicInputs[offset + 2 * i] = addressToField(_headers[i].coinbase);
+      publicInputs[offset + 2 * i + 1] = bytes32(_headers[i].accumulatedFees);
     }
-    offset += feesLength;
+    offset += Constants.MAX_CHECKPOINTS_PER_EPOCH * 2;
 
     publicInputs[offset] = bytes32(block.chainid);
     offset += 1;
@@ -327,6 +331,29 @@ library EpochProofLib {
     ValidatorSelectionLib.verifyAttestations(epoch, _attestations, checkpointLog.payloadDigest);
   }
 
+  /**
+   * @notice Rehashes each provided checkpoint header and requires it to match the stored header hash
+   *
+   * @param _start The first checkpoint number in the epoch (inclusive)
+   * @param _end The last checkpoint number in the epoch (inclusive)
+   * @param _headers The proposed headers for each checkpoint in [_start, _end]
+   */
+  function verifyHeaders(uint256 _start, uint256 _end, ProposedHeader[] calldata _headers) private view {
+    uint256 numCheckpoints = _end - _start + 1;
+    require(
+      _headers.length == numCheckpoints, Errors.Rollup__InvalidCheckpointHeaderCount(numCheckpoints, _headers.length)
+    );
+
+    for (uint256 i = 0; i < numCheckpoints; i++) {
+      bytes32 expectedHeaderHash = STFLib.getHeaderHash(_start + i);
+      bytes32 providedHeaderHash = ProposedHeaderLib.hash(_headers[i]);
+      require(
+        providedHeaderHash == expectedHeaderHash,
+        Errors.Rollup__InvalidCheckpointHeader(expectedHeaderHash, providedHeaderHash)
+      );
+    }
+  }
+
   /**
    * @notice Validates that an epoch proof submission meets all acceptance criteria
    *
@@ -409,7 +436,7 @@ library EpochProofLib {
     BlobLib.validateBatchedBlob(_args.blobInputs);
 
     bytes32[] memory publicInputs =
-      getEpochProofPublicInputs(_args.start, _args.end, _args.args, _args.fees, _args.blobInputs);
+      getEpochProofPublicInputs(_args.start, _args.end, _args.args, _args.headers, _args.blobInputs);
 
     require(rollupStore.config.epochProofVerifier.verify(_args.proof, publicInputs), Errors.Rollup__InvalidProof());
 
```

### l1-contracts/src/core/libraries/rollup/ProposedHeaderLib.sol
```diff
@@ -29,6 +29,7 @@ struct ProposedHeader {
   bytes32 feeRecipient;
   GasFees gasFees;
   uint256 totalManaUsed;
+  uint256 accumulatedFees;
 }
 
 /**
@@ -62,7 +63,8 @@ library ProposedHeaderLib {
         _header.feeRecipient,
         _header.gasFees.feePerDaGas,
         _header.gasFees.feePerL2Gas,
-        _header.totalManaUsed
+        _header.totalManaUsed,
+        _header.accumulatedFees
       )
     );
   }
```

### l1-contracts/src/core/libraries/rollup/RewardLib.sol
```diff
@@ -151,7 +151,7 @@ library RewardLib {
     return accumulatedRewards;
   }
 
-  function handleRewardsAndFees(SubmitEpochRootProofArgs memory _args, Epoch _endEpoch) internal {
+  function handleRewardsAndFees(SubmitEpochRootProofArgs calldata _args, Epoch _endEpoch) internal {
     RollupStore storage rollupStore = STFLib.getStorage();
     RewardStorage storage rewardStorage = getStorage();
 
@@ -215,7 +215,7 @@ library RewardLib {
 
         v.manaUsed = feeHeader.getManaUsed();
 
-        uint256 fee = uint256(_args.fees[1 + i * 2]);
+        uint256 fee = _args.headers[i].accumulatedFees;
         uint256 burn = feeHeader.getCongestionCost() * v.manaUsed;
 
         t.feesToClaim += fee;
@@ -230,7 +230,7 @@ library RewardLib {
         v.sequencerFee = fee - burn - v.proverFee;
 
         {
-          v.sequencer = fieldToAddress(_args.fees[i * 2]);
+          v.sequencer = _args.headers[i].coinbase;
           uint256 toSequencer = v.sequencerCheckpointReward + v.sequencerFee;
           if (toSequencer > 0) {
             rewardStorage.sequencerRewards[v.sequencer] += toSequencer;
@@ -299,8 +299,4 @@ library RewardLib {
       storageStruct.slot := position
     }
   }
-
-  function fieldToAddress(bytes32 _f) private pure returns (address) {
-    return address(uint160(uint256(_f)));
-  }
 }
```

### l1-contracts/src/core/libraries/rollup/RollupOperationsExtLib.sol
```diff
@@ -9,6 +9,7 @@ import {STFLib} from "@aztec/core/libraries/rollup/STFLib.sol";
 import {Timestamp, TimeLib, Slot, Epoch} from "@aztec/core/libraries/TimeLib.sol";
 import {BlobLib} from "@aztec-blob-lib/BlobLib.sol";
 import {EpochProofLib} from "./EpochProofLib.sol";
+import {ProposedHeader} from "@aztec/core/libraries/rollup/ProposedHeaderLib.sol";
 import {AttestationLib} from "@aztec/core/libraries/rollup/AttestationLib.sol";
 import {
   ProposeLib,
@@ -81,10 +82,10 @@ library RollupOperationsExtLib {
     uint256 _start,
     uint256 _end,
     PublicInputArgs calldata _args,
-    bytes32[] calldata _fees,
+    ProposedHeader[] calldata _headers,
     bytes calldata _blobPublicInputs
   ) external view returns (bytes32[] memory) {
-    return EpochProofLib.getEpochProofPublicInputs(_start, _end, _args, _fees, _blobPublicInputs);
+    return EpochProofLib.getEpochProofPublicInputs(_start, _end, _args, _headers, _blobPublicInputs);
   }
 
   function validateBlobs(bytes calldata _blobsInput, bool _checkBlob)
```

### l1-contracts/test/Rollup.t.sol
```diff
@@ -459,6 +459,7 @@ contract RollupTest is RollupBase {
 
       // We mess up the fees and say that someone is paying a massive priority which surpass the amount available.
       interim.feeAmount = interim.manaUsed * interim.minFee + interim.portalBalance;
+      header.accumulatedFees = interim.feeAmount;
 
       // Assert that balance have NOT been increased by proposing the checkpoint
       ProposeArgs memory args = ProposeArgs({header: header, archive: data.archive, oracleInput: OracleInput(0)});
@@ -469,6 +470,8 @@ contract RollupTest is RollupBase {
         attestationsAndSignersSignature,
         data.blobCommitments
       );
+
+      proposedHeaders[1] = header;
       assertEq(testERC20.balanceOf(header.coinbase), 0, "invalid coinbase balance");
     }
 
@@ -487,17 +490,7 @@ contract RollupTest is RollupBase {
           interim.feeAmount
         )
       );
-      _submitEpochProof(
-        1,
-        1,
-        checkpoint.archive,
-        data.archive,
-        data.batchedBlobInputs,
-        data.header.outHash,
-        prover,
-        header.coinbase,
-        interim.feeAmount
-      );
+      _submitEpochProof(1, 1, checkpoint.archive, data.archive, data.batchedBlobInputs, data.header.outHash, prover);
     }
     assertEq(testERC20.balanceOf(header.coinbase), 0, "invalid coinbase balance");
     assertEq(rollup.getSequencerRewards(header.coinbase), 0, "invalid sequencer rewards");
@@ -510,15 +503,7 @@ contract RollupTest is RollupBase {
 
       // When the checkpoint is proven we should have received the funds
       _submitEpochProof(
-        1,
-        1,
-        checkpoint.archive,
-        data.archive,
-        data.batchedBlobInputs,
-        data.header.outHash,
-        address(42),
-        header.coinbase,
-        interim.feeAmount
+        1, 1, checkpoint.archive, data.archive, data.batchedBlobInputs, data.header.outHash, address(42)
       );
 
       {
@@ -897,7 +882,7 @@ contract RollupTest is RollupBase {
     bytes memory _blobInputs,
     bytes32 _outHash
   ) internal {
-    _submitEpochProof(_start, _end, _prevArchive, _archive, _blobInputs, _outHash, address(0), address(0), 0);
+    _submitEpochProof(_start, _end, _prevArchive, _archive, _blobInputs, _outHash, address(0));
   }
 
   function _submitEpochProof(
@@ -907,24 +892,24 @@ contract RollupTest is RollupBase {
     bytes32 _archive,
     bytes memory _blobInputs,
     bytes32 _outHash,
-    address _prover,
-    address _coinbase,
-    uint256 _fee
+    address _prover
   ) internal {
     PublicInputArgs memory args = PublicInputArgs({
       previousArchive: _prevArchive, endArchive: _archive, outHash: _outHash, proverId: _prover
     });
 
-    bytes32[] memory fees = new bytes32[](Constants.MAX_CHECKPOINTS_PER_EPOCH * 2);
-    fees[0] = bytes32(uint256(uint160(bytes20(_coinbase)))); // Need the address to be left padded within the bytes32
-    fees[1] = bytes32(_fee);
+    uint256 size = _end - _start + 1;
+    ProposedHeader[] memory headers = new ProposedHeader[](size);
+    for (uint256 i = 0; i < size; i++) {
+      headers[i] = proposedHeaders[_start + i];
+    }
 
     rollup.submitEpochRootProof(
       SubmitEpochRootProofArgs({
         start: _start,
         end: _end,
         args: args,
-        fees: fees,
+        headers: headers,
         attestations: CommitteeAttestations({signatureIndices: "", signaturesOrAddresses: ""}),
         blobInputs: _blobInputs,
         proof: ""
```

### l1-contracts/test/base/DecoderBase.sol
```diff
@@ -40,6 +40,7 @@ contract DecoderBase is TestBase {
   }
 
   struct AlphabeticalHeader {
+    uint256 accumulatedFees;
     bytes32 blobsHash;
     bytes32 blockHeadersHash;
     address coinbase;
@@ -109,7 +110,8 @@ contract DecoderBase is TestBase {
           coinbase: full.checkpoint.header.coinbase,
           feeRecipient: full.checkpoint.header.feeRecipient,
           gasFees: full.checkpoint.header.gasFees,
-          totalManaUsed: full.checkpoint.header.totalManaUsed
+          totalManaUsed: full.checkpoint.header.totalManaUsed,
+          accumulatedFees: full.checkpoint.header.accumulatedFees
         }),
         headerHash: full.checkpoint.headerHash,
         numTxs: full.checkpoint.numTxs
```

### l1-contracts/test/base/RollupBase.sol
```diff
@@ -15,6 +15,7 @@ import {Timestamp, Slot, Epoch, TimeLib} from "@aztec/core/libraries/TimeLib.sol
 import {DataStructures} from "@aztec/core/libraries/DataStructures.sol";
 import {BlobLib} from "@aztec-blob-lib/BlobLib.sol";
 import {ProposeArgs, OracleInput, ProposeLib} from "@aztec/core/libraries/rollup/ProposeLib.sol";
+import {ProposedHeader} from "@aztec/core/libraries/rollup/ProposedHeaderLib.sol";
 import {
   CommitteeAttestation,
   CommitteeAttestations,
@@ -37,6 +38,7 @@ contract RollupBase is DecoderBase {
   Signature internal attestationsAndSignersSignature;
 
   mapping(uint256 => uint256) internal checkpointFees;
+  mapping(uint256 => ProposedHeader) internal proposedHeaders;
 
   function _proveCheckpoints(string memory _name, uint256 _start, uint256 _end, address _prover) internal {
     _proveCheckpoints(_name, _start, _end, _prover, "");
@@ -79,13 +81,10 @@ contract RollupBase is DecoderBase {
       proverId: _prover
     });
 
-    bytes32[] memory fees = new bytes32[](Constants.MAX_CHECKPOINTS_PER_EPOCH * 2);
-
     uint256 size = endCheckpointNumber - startCheckpointNumber + 1;
+    ProposedHeader[] memory headers = new ProposedHeader[](size);
     for (uint256 i = 0; i < size; i++) {
-      fees[i * 2] = bytes32(uint256(uint160(bytes20(("sequencer"))))); // Need the address to be left padded within the
-        // bytes32
-      fees[i * 2 + 1] = bytes32(uint256(checkpointFees[startCheckpointNumber + i]));
+      headers[i] = proposedHeaders[startCheckpointNumber + i];
     }
 
     // All the way down here if reverting.
@@ -99,7 +98,7 @@ contract RollupBase is DecoderBase {
         start: startCheckpointNumber,
         end: endCheckpointNumber,
         args: args,
-        fees: fees,
+        headers: headers,
         attestations: CommitteeAttestations({signatureIndices: "", signaturesOrAddresses: ""}),
         blobInputs: endFull.checkpoint.batchedBlobInputs,
         proof: ""
@@ -155,6 +154,10 @@ contract RollupBase is DecoderBase {
     uint128 minFee = SafeCast.toUint128(rollup.getManaMinFeeAt(full.checkpoint.header.timestamp, true));
     full.checkpoint.header.gasFees.feePerL2Gas = minFee;
     full.checkpoint.header.totalManaUsed = _manaUsed;
+    full.checkpoint.header.accumulatedFees = _manaUsed * minFee;
+    // Sequencer rewards are credited to the verified header's coinbase, so pin it to a known address tests can assert
+    // on.
+    full.checkpoint.header.coinbase = address(bytes20("sequencer"));
 
     checkpointFees[full.checkpoint.checkpointNumber] = _manaUsed * minFee;
 
@@ -190,6 +193,8 @@ contract RollupBase is DecoderBase {
       }
     }
 
+    proposedHeaders[full.checkpoint.checkpointNumber] = full.checkpoint.header;
+
     ProposeArgs memory args =
       ProposeArgs({header: full.checkpoint.header, archive: full.checkpoint.archive, oracleInput: OracleInput(0)});
 
```

### l1-contracts/test/benchmark/happy.t.sol
```diff
@@ -147,6 +147,8 @@ contract BenchmarkRollupTest is FeeModelTestPoints, DecoderBase {
   // Track attestations by checkpoint number for proof submission
   mapping(uint256 => CommitteeAttestations) internal checkpointAttestations;
 
+  mapping(uint256 => ProposedHeader) internal checkpointHeaders;
+
   Multicall3 internal multicall = new Multicall3();
 
   address internal slashingProposer;
@@ -270,6 +272,7 @@ contract BenchmarkRollupTest is FeeModelTestPoints, DecoderBase {
     header.feeRecipient = bytes32(0);
     header.gasFees.feePerL2Gas = manaMinFee;
     header.totalManaUsed = manaSpent;
+    header.accumulatedFees = uint256(manaMinFee) * manaSpent;
 
     ProposeArgs memory proposeArgs = ProposeArgs({
       header: header,
@@ -449,9 +452,10 @@ contract BenchmarkRollupTest is FeeModelTestPoints, DecoderBase {
 
         skipBlobCheck(address(rollup));
 
-        // Store the attestations for the current checkpoint number
+        // Store the attestations and header for the current checkpoint number
         uint256 currentCheckpointNumber = rollup.getPendingCheckpointNumber() + 1;
         checkpointAttestations[currentCheckpointNumber] = AttestationLibHelper.packAttestations(b.attestations);
+        checkpointHeaders[currentCheckpointNumber] = b.proposeArgs.header;
 
         if (_slashing == TestSlash.TALLY) {
           SlashRound slashRound = SlashingProposer(slashingProposer).getCurrentRound();
@@ -496,16 +500,9 @@ contract BenchmarkRollupTest is FeeModelTestPoints, DecoderBase {
           epochSize++;
         }
 
-        bytes32[] memory fees = new bytes32[](Constants.MAX_CHECKPOINTS_PER_EPOCH * 2);
-
-        for (uint256 feeIndex = 0; feeIndex < epochSize; feeIndex++) {
-          // we need the minFee, and we cannot just take it from the point. Because it is different
-          Timestamp ts = rollup.getTimestampForSlot(Slot.wrap(start + feeIndex));
-          uint256 manaMinFee = rollup.getManaMinFeeAt(ts, true);
-          uint256 fee = rollup.getFeeHeader(start + feeIndex).manaUsed * manaMinFee;
-
-          fees[feeIndex * 2] = bytes32(uint256(uint160(bytes20(coinbase))));
-          fees[feeIndex * 2 + 1] = bytes32(fee);
+        ProposedHeader[] memory headers = new ProposedHeader[](epochSize);
+        for (uint256 headerIndex = 0; headerIndex < epochSize; headerIndex++) {
+          headers[headerIndex] = checkpointHeaders[start + headerIndex];
         }
 
         CheckpointLog memory endCheckpoint = rollup.getCheckpoint(start + epochSize - 1);
@@ -522,7 +519,7 @@ contract BenchmarkRollupTest is FeeModelTestPoints, DecoderBase {
             start: start,
             end: start + epochSize - 1,
             args: args,
-            fees: fees,
+            headers: headers,
             attestations: checkpointAttestations[start + epochSize - 1],
             blobInputs: full.checkpoint.batchedBlobInputs,
             proof: ""
```

### l1-contracts/test/compression/PreHeating.t.sol
```diff
@@ -137,6 +137,8 @@ contract PreHeatingTest is FeeModelTestPoints, DecoderBase {
   // Track attestations by checkpoint number for proof submission
   mapping(uint256 => CommitteeAttestations) internal checkpointAttestations;
 
+  mapping(uint256 => ProposedHeader) internal checkpointHeaders;
+
   modifier prepare(uint256 _validatorCount, uint256 _targetCommitteeSize) {
     // We deploy a the rollup and sets the time and all to
     vm.warp(l1Metadata[0].timestamp - SLOT_DURATION);
@@ -220,9 +222,10 @@ contract PreHeatingTest is FeeModelTestPoints, DecoderBase {
 
         skipBlobCheck(address(rollup));
 
-        // Store the attestations for the current checkpoint number
+        // Store the attestations and header for the current checkpoint number
         uint256 currentCheckpointNumber = rollup.getPendingCheckpointNumber() + 1;
         checkpointAttestations[currentCheckpointNumber] = AttestationLibHelper.packAttestations(b.attestations);
+        checkpointHeaders[currentCheckpointNumber] = b.proposeArgs.header;
 
         vm.prank(proposer);
         rollup.propose(
@@ -249,16 +252,9 @@ contract PreHeatingTest is FeeModelTestPoints, DecoderBase {
           epochSize++;
         }
 
-        bytes32[] memory fees = new bytes32[](Constants.MAX_CHECKPOINTS_PER_EPOCH * 2);
-
-        for (uint256 feeIndex = 0; feeIndex < epochSize; feeIndex++) {
-          // we need the minFee, and we cannot just take it from the point. Because it is different
-          Timestamp ts = rollup.getTimestampForSlot(Slot.wrap(start + feeIndex));
-          uint256 manaMinFee = rollup.getManaMinFeeAt(ts, true);
-          uint256 fee = rollup.getFeeHeader(start + feeIndex).manaUsed * manaMinFee;
-
-          fees[feeIndex * 2] = bytes32(uint256(uint160(bytes20(coinbase))));
-          fees[feeIndex * 2 + 1] = bytes32(fee);
+        ProposedHeader[] memory headers = new ProposedHeader[](epochSize);
+        for (uint256 headerIndex = 0; headerIndex < epochSize; headerIndex++) {
+          headers[headerIndex] = checkpointHeaders[start + headerIndex];
         }
 
         CheckpointLog memory endCheckpoint = rollup.getCheckpoint(start + epochSize - 1);
@@ -276,7 +272,7 @@ contract PreHeatingTest is FeeModelTestPoints, DecoderBase {
               start: start,
               end: start + epochSize - 1,
               args: args,
-              fees: fees,
+              headers: headers,
               attestations: checkpointAttestations[start + epochSize - 1],
               blobInputs: full.checkpoint.batchedBlobInputs,
               proof: ""
@@ -327,6 +323,7 @@ contract PreHeatingTest is FeeModelTestPoints, DecoderBase {
     header.feeRecipient = bytes32(0);
     header.gasFees.feePerL2Gas = manaMinFee;
     header.totalManaUsed = manaSpent;
+    header.accumulatedFees = uint256(manaMinFee) * manaSpent;
 
     ProposeArgs memory proposeArgs = ProposeArgs({
       header: header,
```
