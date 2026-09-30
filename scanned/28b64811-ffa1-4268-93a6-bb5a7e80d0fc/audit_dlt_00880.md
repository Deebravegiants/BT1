# [?] fix(protocol): add sub image id into ZK aggregation proof verification to prevent security issue (#20916)

## Summary
Severity: Unknown
Chain: Taiko
Component: taikoxyz/taiko-mono
Published: 2025-12-15
Source: https://github.com/taikoxyz/taiko-mono/commit/d5b904f71f202bf662e75d3a4894a17b99a0a2ae
Type: security-commit

## Details
fix(protocol): add sub image id into ZK aggregation proof verification to prevent security issue (#20916)

Co-authored-by: Gustavo Gonzalez <gustavo@taiko.xyz>
Co-authored-by: Gustavo Gonzalez <ggonzalezsomer@gmail.com>

## Patch
### packages/protocol/contracts/layer1/verifiers/LibPublicInput.sol
```diff
@@ -35,6 +35,22 @@ library LibPublicInput {
         );
     }
 
+    /// @dev Hashes the public input for the ZK aggregation proof verification,
+    ///         which contains the sub image id to be aggregated for security.
+    /// @param _blockProvingProgram The proving program identifier.
+    /// @param _aggregatedProvingHash The aggregated proving hash from the inbox.
+    /// @return The ZK aggregation public input hash.
+    function hashZKAggregationPublicInputs(
+        bytes32 _blockProvingProgram,
+        bytes32 _aggregatedProvingHash
+    )
+        internal
+        pure
+        returns (bytes32)
+    {
+        return EfficientHashLib.hash(_blockProvingProgram, _aggregatedProvingHash);
+    }
+
     // ---------------------------------------------------------------
     // Errors
     // ---------------------------------------------------------------
```

### packages/protocol/contracts/layer1/verifiers/Risc0Verifier.sol
```diff
@@ -71,8 +71,11 @@ contract Risc0Verifier is IProofVerifier, Ownable2Step {
             _aggregatedProvingHash, address(this), address(0), taikoChainId
         );
 
+        bytes32 r0AggregationPublicInput =
+            LibPublicInput.hashZKAggregationPublicInputs(blockImageId, publicInput);
+
         // journalDigest is the sha256 hash of the hashed public input
-        bytes32 journalDigest = sha256(abi.encodePacked(publicInput));
+        bytes32 journalDigest = sha256(abi.encodePacked(r0AggregationPublicInput));
 
         // call risc0 verifier contract
         (bool success,) = riscoGroth16Verifier.staticcall(
```

### packages/protocol/contracts/layer1/verifiers/SP1Verifier.sol
```diff
@@ -67,11 +67,14 @@ contract SP1Verifier is IProofVerifier, Ownable2Step {
             _aggregatedProvingHash, address(this), address(0), taikoChainId
         );
 
+        bytes32 sp1AggregationPublicInput =
+            LibPublicInput.hashZKAggregationPublicInputs(blockProvingProgram, publicInput);
+
         // _proof[64:] is the succinct's proof position
         (bool success,) = sp1RemoteVerifier.staticcall(
             abi.encodeCall(
                 ISP1Verifier.verifyProof,
-                (aggregationProgram, abi.encodePacked(publicInput), _proof[64:])
+                (aggregationProgram, abi.encodePacked(sp1AggregationPublicInput), _proof[64:])
             )
         );
 
```

### packages/protocol/gas-reports/layer1-contracts.txt
```diff
@@ -120,14 +120,14 @@ Risc0VerifierTest:test_setImageIdTrusted_EmitsAndUpdates() (gas: 36792)
 Risc0VerifierTest:test_verifyProof_RevertWhen_AggregatedHashZero() (gas: 61165)
 Risc0VerifierTest:test_verifyProof_RevertWhen_AggregationImageUntrusted() (gas: 11842)
 Risc0VerifierTest:test_verifyProof_RevertWhen_BlockImageUntrusted() (gas: 38570)
-Risc0VerifierTest:test_verifyProof_RevertWhen_RemoteVerifierFails() (gas: 64833)
-Risc0VerifierTest:test_verifyProof_SucceedsAndCallsRemoteVerifier() (gas: 65342)
+Risc0VerifierTest:test_verifyProof_RevertWhen_RemoteVerifierFails() (gas: 65083)
+Risc0VerifierTest:test_verifyProof_SucceedsAndCallsRemoteVerifier() (gas: 65594)
 SP1VerifierTest:test_setProgramTrusted_UpdatesMapping() (gas: 36742)
 SP1VerifierTest:test_verifyProof_RevertWhen_AggregationNotTrusted() (gas: 38187)
 SP1VerifierTest:test_verifyProof_RevertWhen_BlockProgramNotTrusted() (gas: 38407)
 SP1VerifierTest:test_verifyProof_RevertWhen_ProofTooShort() (gas: 8903)
-SP1VerifierTest:test_verifyProof_RevertWhen_RemoteVerifierFails() (gas: 63997)
-SP1VerifierTest:test_verifyProof_Succeeds() (gas: 64068)
+SP1VerifierTest:test_verifyProof_RevertWhen_RemoteVerifierFails() (gas: 64245)
+SP1VerifierTest:test_verifyProof_Succeeds() (gas: 64318)
 SgxVerifierTest:test_addInstances_RevertWhen_DuplicateAddress() (gas: 86497)
 SgxVerifierTest:test_addInstances_StoresEntries() (gas: 140245)
 SgxVerifierTest:test_deleteInstances_RemovesInstance() (gas: 118327)
```

### packages/protocol/test/layer1/verifiers/Risc0Verifier.t.sol
```diff
@@ -61,7 +61,9 @@ contract Risc0VerifierTest is Test {
         bytes32 publicInput = LibPublicInput.hashPublicInputs(
             bytes32(uint256(1)), address(verifier), address(0), CHAIN_ID
         );
-        bytes32 journalDigest = sha256(abi.encodePacked(publicInput));
+        bytes32 r0AggregationPublicInput =
+            LibPublicInput.hashZKAggregationPublicInputs(BLOCK_IMAGE_ID, publicInput);
+        bytes32 journalDigest = sha256(abi.encodePacked(r0AggregationPublicInput));
 
         vm.mockCallRevert(
             REMOTE,
@@ -81,7 +83,9 @@ contract Risc0VerifierTest is Test {
         bytes32 publicInput = LibPublicInput.hashPublicInputs(
             bytes32(uint256(1)), address(verifier), address(0), CHAIN_ID
         );
-        bytes32 journalDigest = sha256(abi.encodePacked(publicInput));
+        bytes32 r0AggregationPublicInput =
+            LibPublicInput.hashZKAggregationPublicInputs(BLOCK_IMAGE_ID, publicInput);
+        bytes32 journalDigest = sha256(abi.encodePacked(r0AggregationPublicInput));
 
         vm.expectCall(
             REMOTE,
```

### packages/protocol/test/layer1/verifiers/SP1Verifier.t.sol
```diff
@@ -62,12 +62,14 @@ contract SP1VerifierTest is Test {
         bytes32 publicInput = LibPublicInput.hashPublicInputs(
             bytes32(uint256(1)), address(verifier), address(0), CHAIN_ID
         );
+        bytes32 sp1AggregationPublicInput =
+            LibPublicInput.hashZKAggregationPublicInputs(PROGRAM_VKEY, publicInput);
 
         vm.mockCallRevert(
             REMOTE,
             abi.encodeCall(
                 ISP1Verifier.verifyProof,
-                (AGGREGATION_VKEY, abi.encodePacked(publicInput), succinctProof)
+                (AGGREGATION_VKEY, abi.encodePacked(sp1AggregationPublicInput), succinctProof)
             ),
             "fail"
         );
@@ -85,10 +87,12 @@ contract SP1VerifierTest is Test {
         bytes32 publicInput = LibPublicInput.hashPublicInputs(
             bytes32(uint256(1)), address(verifier), address(0), CHAIN_ID
         );
+        bytes32 sp1AggregationPublicInput =
+            LibPublicInput.hashZKAggregationPublicInputs(PROGRAM_VKEY, publicInput);
 
         bytes memory expectedCall = abi.encodeCall(
             ISP1Verifier.verifyProof,
-            (AGGREGATION_VKEY, abi.encodePacked(publicInput), succinctProof)
+            (AGGREGATION_VKEY, abi.encodePacked(sp1AggregationPublicInput), succinctProof)
         );
 
         vm.expectCall(REMOTE, expectedCall);
```
