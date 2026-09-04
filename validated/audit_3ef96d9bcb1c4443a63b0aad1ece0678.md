Based on my investigation, I was unable to fully verify the implementation of `rootHashExists` in `MerkleBase.sol` before running out of tool calls, so I can only confirm the root-cause data-flow issue, not the exact exploitability of the downstream Merkle lookup. I'll present what is solidly confirmed and flag the remaining uncertainty explicitly.

### Title
`rootHashHinkalIndex` is unauthenticated by the proof, `calldataHash`, or `signedMessageHash` - ([File: contracts/Hinkal.sol])

### Summary
`CircomData.rootHashHinkalIndex` is passed by an unprivileged caller and used directly in the on-chain root-history lookup in `transact()`, but this field is never included in the circuit's public-input vector, the `calldataHash` integrity check, or the `getSignedMessageHash` binding, meaning the value used to validate root freshness/position is completely uncommitted by the ZK proof or by the transaction signer.

### Finding Description
`CircomData` declares `rootHashHinkalIndex` alongside `rootHashHinkal` [1](#0-0) . In `Hinkal.transact()`, after the ZK proof is verified against `inputForCircom`, the contract separately validates the root via `rootHashExists(circomData.rootHashHinkal, circomData.rootHashHinkalIndex)` [2](#0-1) .

However, tracing every place `CircomData` fields are bound to the proof/signature:
- `getHashedCalldata1`/`getHashedCalldata2` (which produce `circomData.calldataHash`) include `publicSignalCount`, `relay`, `emporiumMessage`, `externalActionData`, `slippageValues`, `hookData`, `encryptedOutputs`, `onChainEncryptedOutput`, `feeStructure`, `onChainCreation`, `originalSender`, `extraData` — but not `rootHashHinkalIndex` [3](#0-2) .
- `getSignedMessageHash` binds `rootHashHinkal`, token addresses, amount changes, nullifiers, commitments, `calldataHash`, stealth-address fields — again no `rootHashHinkalIndex` [4](#0-3) .
- `formBasicInput`, which builds the actual public-input vector fed into `verifyProof`, lists `rootHashHinkal` and the signed-message hash but never `rootHashHinkalIndex` [5](#0-4) .
- `performHinkalChecks` in `HinkalHelper.sol` re-checks `calldataHash` integrity, relay validity, and dimensions, but never touches `rootHashHinkalIndex` [6](#0-5) .

So `rootHashHinkalIndex` is a raw, attacker-supplied calldata value that is used only in `rootHashExists` at the moment of root validation, with no prover commitment or relay/EIP-712 signature binding it to a specific transaction. This matches the analog category "a CircomData field acted on but outside `calldataHash` / `signedMessageHash` / the public-input vector."

### Impact Explanation
Whether this is exploitable to break the root equality (i.e., get the contract to accept a `(leaf, root)`/nullifier state the tree never actually produced, or accept a stale/incorrect root as current) depends entirely on how `MerkleBase.rootHashExists(root, index)` uses `index` — e.g., whether it uses the index merely as an array-lookup hint that is still validated against `root`, or whether index-based logic (bounds, "recent roots window", zero-initialized slots) can be abused to make a non-current or fabricated root appear valid. I located `rootHashExists` calls in `contracts/Hinkal.sol`, `contracts/MerkleBase.sol`, and `contracts/types/IMerkle.sol`, but did not get to read the body of `MerkleBase.rootHashExists` before the tool budget ran out, so I cannot confirm whether the index parameter can be abused to accept a stale/incorrect root, which would be required to actually break the balance/nullifier equality (Critical: proof/root verification bypass) versus being a harmless internal array index that is fully re-validated against the supplied root value (no impact).

### Likelihood Explanation
Any unprivileged EOA can freely choose `rootHashHinkalIndex` in the calldata since it is not covered by any hash or signature check that a relay or the protocol enforces before proof verification, and to route the transaction as-is only requires a valid proof for the chosen `rootHashHinkal` value. The remaining condition for exploitation is dependent on `MerkleBase.rootHashExists`'s internal semantics, which is unverified here.

### Recommendation
1. Have the engineering team review `MerkleBase.rootHashExists(root, index)` to confirm whether `index` can cause acceptance of a root not currently valid/most-recent (e.g., stale root replay, off-by-one on the rolling root buffer, or an uninitialized/default slot).
2. If `index` affects acceptance criteria beyond a plain lookup that's still fully validated by matching `root`, bind `rootHashHinkalIndex` into `calldataHash`/`signedMessageHash` (or otherwise make it derivable/re-computed on-chain rather than caller-supplied) so it cannot be manipulated independently of the proven root.

### Proof of Concept
Cannot be finalized without confirming `MerkleBase.rootHashExists`'s semantics for `index`. The concrete PoC would be: craft a valid proof for some `rootHashHinkal` value R that was valid at an earlier point in history (or a placeholder value at an uninitialized slot), submit `transact()` with `rootHashHinkalIndex` pointing at a stale/uninitialized slot, and observe whether `rootHashExists` incorrectly returns `true`, allowing the transaction (and associated nullifier insertion) to proceed against a `(leaf, root)` pair inconsistent with the tree's actual current state.

### Citations

**File:** contracts/types/CircomData.sol (L24-25)
```text
    uint256 rootHashHinkal;
    uint256 rootHashHinkalIndex;
```

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

**File:** contracts/CircomDataBuilder.sol (L180-240)
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

        for (uint16 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            input[index++] = uint256(
                uint160(circomData.erc20TokenAddresses[i])
            );
        }

        for (uint16 i = 0; i < circomData.amountChanges.length; i++) {
            require(
                circomData.amountChanges[i] < MAX_AMOUNT &&
                    circomData.amountChanges[i] > -1 * MAX_AMOUNT,
                "amount changed is too large"
            );

            input[index++] = circomData.amountChanges[i] >= 0
                ? uint256(circomData.amountChanges[i])
                : CIRCOM_P - uint256(-circomData.amountChanges[i]);
        }

        for (uint16 i = 0; i < circomData.inputNullifiers.length; i++) {
            for (uint16 j = 0; j < circomData.inputNullifiers[i].length; j++) {
                input[index++] = circomData.inputNullifiers[i][j];
            }
        }

        input[index++] = circomData.timeStamp;

        for (uint16 i = 0; i < circomData.outCommitments.length; i++) {
            for (uint16 j = 0; j < circomData.outCommitments[i].length; j++) {
                input[index++] = circomData.outCommitments[i][j];
            }
        }
        input[index++] = circomData.calldataHash;

        input[index++] = circomData.stealthAddressStructure.H0x;
        input[index++] = circomData.stealthAddressStructure.H0y;

        return input;
    }
```

**File:** contracts/HinkalHelper.sol (L208-236)
```text
    function performHinkalChecks(
        CircomData calldata circomData,
        Dimensions calldata dimensions,
        address sender
    ) external view returns (uint256[] memory) {
        require(
            (circomData.originalSender == address(0) &&
                circomData.relay != address(0)) ||
                (circomData.originalSender == sender &&
                    circomData.relay == address(0)),
            "invalid value for originalSender"
        );

        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
        relayerIsValid(circomData.relay);
        dimensionsCheck(circomData, dimensions);
        checkOnchainCreation(circomData);

        return
            CircomDataBuilder.formInputForCircom(
                block.chainid,
                hinkalAddress,
                circomData
            );
    }
```
