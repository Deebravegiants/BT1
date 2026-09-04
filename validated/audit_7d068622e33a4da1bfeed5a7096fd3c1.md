### Title
`rootHashHinkalIndex` is used to select the historical Merkle root but is never bound to the proof or the calldata-integrity hash - ([File: contracts/CircomDataBuilder.sol], [File: contracts/Hinkal.sol])

### Summary
`CircomData.rootHashHinkalIndex` is consumed on-chain to look up which historical root the ZK proof is claimed to have been generated against, but this field is never committed to by the ZK proof's public-input vector, the `calldataHash`, or the `signedMessageHash`. Every other security-relevant field in `CircomData` is folded into one of these three integrity anchors; `rootHashHinkalIndex` is the sole exception.

### Finding Description
`Hinkal.transact` uses the caller-supplied index together with the caller-supplied root to validate the Merkle root the proof was built against: [1](#0-0) 

The proof-binding logic in `CircomDataBuilder` builds three independent integrity anchors that are supposed to cover every field of `CircomData`:
- `getHashedCalldata1`/`getHashedCalldata2`, which is checked against `circomData.calldataHash` in `HinkalHelper.performHinkalChecks`: [2](#0-1) [3](#0-2) 

- `getSignedMessageHash`, which folds in `rootHashHinkal` (the root value itself) but not `rootHashHinkalIndex`: [4](#0-3) 

- the public-input vector built by `formBasicInput`, which also only carries `rootHashHinkal`, never `rootHashHinkalIndex`: [5](#0-4) 

Because `rootHashHinkalIndex` appears in none of `getHashedCalldata1`, `getHashedCalldata2`, `getSignedMessageHash`, or `formBasicInput`'s `input` array, a caller (the relayer, or the `msg.sender` in the self-relay path) can freely choose any index value at call time without invalidating the proof or the `calldataHash` check - only the paired `rootHashHinkal` value is constrained (via `getSignedMessageHash`, which becomes part of the public-input vector). This means the mapping between "which slot in the root-history buffer" and "which root value" that `rootHashExists` is supposed to enforce is not actually authenticated end-to-end; only the root value is authenticated, not its claimed position.

This matches the analog class of "a (leaf, root) pair the circuit accepts that the tree never produced" in spirit: here it is a (root, index) pair whose *pairing* is never checked by the proof, only the root half is checked, and the index half is taken from raw calldata with no cryptographic binding.

### Impact Explanation
If the underlying root-history structure (`Merkle`/`MerkleBase`, not fully inspectable within the tool budget of this session) implements `rootHashExists` as a fixed-size ring buffer indexed by `rootHashHinkalIndex`, an unconstrained index is a well-known source of root-history bypass bugs (e.g., stale/overwritten slots, uninitialized zero slots, or off-by-one wraparound acceptance) in Merkle-root-history designs. If any such implementation detail allows `rootHashExists(root, index)` to return `true` for an `(root, index)` pair the tree state machine never actually produced together, an attacker could get a proof accepted against a root that should be considered invalid/stale for that particular tree position, potentially enabling proof/root verification bypass. This would map to the Critical category ("proof or nullifier verification bypass").

### Likelihood Explanation
Medium-to-Low confidence: I could not verify the exact implementation of `rootHashExists` in `Merkle.sol`/`MerkleBase.sol` within this session's tool budget, so I cannot confirm whether the ring-buffer/lookup logic actually mishandles out-of-range or stale indices. The root cause I *can* prove concretely is that `rootHashHinkalIndex` is structurally unauthenticated by the proof system - which is a real gap regardless of whether the current `Merkle.sol` implementation happens to be safe against it. Any future change to the root-history storage (e.g., switching to a smaller ring buffer, or adding index-dependent decoding) would silently reintroduce/expose this as an exploitable root-verification bypass, since nothing in the proof pipeline constrains the field.

### Recommendation
Include `circomData.rootHashHinkalIndex` in the `getSignedMessageHash` computation (or in `calldataHash1`/`calldataHash2`) so that the specific (root, index) pairing the proof was generated against is cryptographically bound end-to-end, matching how `rootHashHinkal` itself is already protected in `contracts/CircomDataBuilder.sol:104-119`.

### Proof of Concept
1. Generate a valid proof/signature for a transaction using the correct `rootHashHinkal` at its true historical index `i`.
2. At submission time, replace `circomData.rootHashHinkalIndex` with a different index `j` in the calldata passed to `Hinkal.transact`.
3. Because `rootHashHinkalIndex` is absent from `getHashedCalldata1`/`getHashedCalldata2` (contracts/CircomDataBuilder.sol:20-54) and from `getSignedMessageHash`/`formBasicInput` (contracts/CircomDataBuilder.sol:97-132, 180-201), neither the `calldataHash` check in `HinkalHelper.performHinkalChecks` (contracts/HinkalHelper.sol:221-225) nor the Groth16 `verifyProof` call rejects this substitution.
4. Execution proceeds to `rootHashExists(circomData.rootHashHinkal, j)` (contracts/Hinkal.sol:58-64) with an index value that was never validated by the proof - whether this succeeds depends on the concrete `rootHashExists` implementation, which I was unable to fully inspect in this session.

**Note:** I was unable to review `contracts/Merkle.sol` / `contracts/MerkleBase.sol` (the `rootHashExists`/root-history implementation) before the tool budget for this session ran out. Confirming or ruling out actual exploitability requires inspecting those files to determine whether stale/duplicate/uninitialized entries can appear in the root-history structure at attacker-chosen indices.

### Citations

**File:** contracts/Hinkal.sol (L57-64)
```text
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
```

**File:** contracts/CircomDataBuilder.sol (L20-54)
```text
    function getHashedCalldata1(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.publicSignalCount,
                        circomData.relay,
                        circomData.emporiumMessage,
                        circomData.externalActionData,
                        circomData.slippageValues
                    )
                )
            );
    }

    function getHashedCalldata2(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        return
            uint256(
                keccak256(
                    abi.encode(
                        circomData.hookData,
                        circomData.encryptedOutputs,
                        circomData.onChainEncryptedOutput,
                        circomData.feeStructure,
                        circomData.onChainCreation,
                        circomData.originalSender,
                        circomData.extraData
                    )
                )
            );
    }
```

**File:** contracts/CircomDataBuilder.sol (L97-132)
```text
    function getSignedMessageHash(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256 emporiumMessage
    ) internal pure returns (uint256) {
        // split into two encode calls to avoid "stack too deep"
        uint256 hash1 = uint256(
            keccak256(
                abi.encode(
                    chainId,
                    verifyingContract,
                    circomData.rootHashHinkal,
                    _encodeTokenAddresses(circomData.erc20TokenAddresses),
                    _encodeAmountChanges(circomData.amountChanges),
                    circomData.timeStamp,
                    _flatUint256Matrix(circomData.inputNullifiers),
                    _flatUint256Matrix(circomData.outCommitments),
                    circomData.calldataHash,
                    emporiumMessage
                )
            )
        );
        uint256 hash2 = uint256(
            keccak256(
                abi.encode(
                    circomData.stealthAddressStructure.H1x,
                    circomData.stealthAddressStructure.H1y,
                    circomData.stealthAddressStructure.H0x,
                    circomData.stealthAddressStructure.H0y
                )
            )
        );
        return
            uint256(keccak256(abi.encode(hash1, hash2))) % CIRCOM_P;
    }
```

**File:** contracts/CircomDataBuilder.sol (L180-201)
```text
    function formBasicInput(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData,
        uint256[] memory input,
        uint256 index,
        uint256 emporiumMessage
    ) internal pure returns (uint256[] memory) {
        // 1) First we list public inputs as in the body of the main template (not the one with exact dimensions)
        input[index++] = circomData.stealthAddressStructure.H1x;
        input[index++] = circomData.stealthAddressStructure.H1y;
        input[index++] = circomData.stealthAddressStructure.stealthAddress;
        input[index++] = emporiumMessage; // this is for Emporium message signature verification

        // 2) Then we list the private inputs as in the body of the main template
        input[index++] = circomData.rootHashHinkal;
        input[index++] = getSignedMessageHash(
            chainId,
            verifyingContract,
            circomData,
            emporiumMessage
        );
```

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```
