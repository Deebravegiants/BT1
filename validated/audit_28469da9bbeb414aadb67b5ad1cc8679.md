## Finding: `rootHashHinkalIndex` is used to select the Merkle root but is not bound by `calldataHash`, `signedMessageHash`, or the ZK public-input vector

### Summary
`CircomData.rootHashHinkalIndex` is read and acted upon in `Hinkal.transact()` to look up which historical root to compare against, but this field is never included in the two integrity anchors that are supposed to bind every `CircomData` field to the user's authorization: the `calldataHash` and the `signedMessageHash`, nor is it part of the public-input vector passed into the Groth16 verifier.

### Finding Description
`Hinkal.transact()` validates the proof and then separately checks the root: [1](#0-0) 

The root value `circomData.rootHashHinkal` is bound to the user's authorization because it is folded into `getSignedMessageHash` (hash1) and appears in the circuit's public input vector via `formBasicInput`: [2](#0-1) [3](#0-2) 

But `circomData.rootHashHinkalIndex` — the second argument passed to `rootHashExists` — appears nowhere in `getHashedCalldata1`/`getHashedCalldata2` (which together form `calldataHash`): [4](#0-3) 

nor in `getSignedMessageHash`, nor in `formBasicInput`/`formInputEmporiumMin` (the public-input vector fed to the verifier): [5](#0-4) [6](#0-5) 

`HinkalHelper.performHinkalChecks` only re-derives `calldataHash` and re-checks dimensions/relay/on-chain-creation constraints — it never touches `rootHashHinkalIndex`: [7](#0-6) 

This is precisely the analog class called out in the report: a data field that is acted upon on-chain (used to select which stored root to compare) but sits outside every authenticity check (`calldataHash`, `signedMessageHash`, public-input vector) — mirroring the report's core complaint that a configuration/parameter value is trusted and consumed without being validated/bound to the intended semantics.

### Impact Explanation
Whether this is exploitable to break the "(leaf, root) pair the tree never produced" equality depends entirely on the implementation of `rootHashExists(root, index)` in the `Merkle`/`HinkalBase` layer (e.g., whether it does `roots[index] == root` with strict bounds checking versus a linear scan fallback, and whether stale/overwritten ring-buffer slots can coincide with an attacker-chosen `index`). I was not able to load that implementation within the available tool budget, so I cannot confirm a concrete bypass of the equality (e.g., accepting a root that was never actually the root at that historical position, or accepting index 0 / a default storage slot as a false positive). Because `transact()` can be invoked by any relay/caller carrying a previously-signed `circomData` (the field is not part of what the signer authorized), an attacker who can call `transact()` has free choice over `rootHashHinkalIndex` for a given valid `rootHashHinkal`.

### Likelihood Explanation
Any unprivileged actor who submits a `transact()` call (including a relay, which need not be the original prover/signer for the `rootHashHinkalIndex` field specifically) can set `rootHashHinkalIndex` to any value without invalidating the proof, the `calldataHash` check, or the EdDSA-signed message. Exploitability further requires a weakness in the concrete `rootHashExists` lookup logic that I could not verify in this session.

### Recommendation
Include `rootHashHinkalIndex` in either `calldataHash` (via `getHashedCalldata1`/`getHashedCalldata2`) or `signedMessageHash`, and/or have `rootHashExists` perform a defensive `roots[index] == root` check with correct bounds handling and no reliance on unauthenticated caller input to select storage slots. Ensure that the index used to look up historical roots cannot be freely chosen by an unauthorized caller independent of what the prover/signer committed to.

### Proof of Concept
Could not be fully constructed without access to the `Merkle.sol`/`HinkalBase.sol` `rootHashExists` implementation (index-to-root storage lookup logic), which was not retrievable within the remaining tool budget. The root-cause evidence (the field being consumed at `contracts/Hinkal.sol:58-64` while being absent from all three integrity/authorization mechanisms in `contracts/CircomDataBuilder.sol`) is established above, but confirming a concrete state where `rootHashExists` returns `true` for a `(root, index)` pair the tree never actually produced at that index requires reviewing that function's source, which I recommend a follow-up session (or a Devin session with full repo/file access) verify directly.

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
