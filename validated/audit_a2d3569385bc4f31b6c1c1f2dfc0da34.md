### Title
`onChainCreation` flag array is unauthenticated by `calldataHash`/`signedMessageHash` and public-input vector, allowing balance-equation and nullifier bypass - (File: `contracts/CircomDataBuilder.sol`, `contracts/Hinkal.sol`, `contracts/HinkalBase.sol`)

### Summary
`CircomData.onChainCreation` is a `bool[]` that gates two security-critical behaviors: (1) whether the nullifier-uniqueness check is applied for a token's inputs in `insertNullifiers`, and (2) whether `_calculateDeltaAmount`/the balance-equation in `Hinkal.transact` treats the required off-chain amount change as `0` instead of `circomData.amountChanges[i]`. Unlike almost every other field of `CircomData`, `onChainCreation` is never hashed into `calldataHash` (`getHashedCalldata1`/`getHashedCalldata2`), never folded into `signedMessageHash` (`getSignedMessageHash`), and never placed into the circuit's public-input vector (`formBasicInput`/`formInputEmporiumMin`). It is therefore not bound by the prover's signature nor checked by the SNARK verifier — it is a plain, attacker-controlled calldata array that only a same-transaction sanity check (`checkOnchainCreation`) constrains.

### Finding Description
`CircomDataBuilder.getHashedCalldata1`/`getHashedCalldata2` hash exactly these `CircomData` fields into `calldataHash`: [1](#0-0) 

`onChainCreation` is absent from both lists. It is likewise absent from `getSignedMessageHash`'s two hash inputs and from `formBasicInput`, which enumerates every value fed to the circuit's public-input vector: [2](#0-1) [3](#0-2) 

`performHinkalChecks` only verifies that `getHashedCalldata(circomData) == circomData.calldataHash` — since `onChainCreation` isn't part of that hash, this check does not constrain it: [4](#0-3) 

The only guard on `onChainCreation` is `checkOnchainCreation`, which merely requires that when `onChainCreation[i]==true`, `amountChanges[i]==0` and all `inputNullifiers[i][j]==0` for that token, and forbids it for external actions: [5](#0-4) 

But `onChainCreation` itself directly changes two equalities enforced in `Hinkal.transact`:

1. **Balance equation** — the required balance delta uses `0` instead of `circomData.amountChanges[i]` when `onChainCreation[i]` is true: [6](#0-5) 

2. **Nullifier-skip in `insertNullifiers`** — when `onChainCreation[i]==true`, the entire inner loop `break`s and the nullifier uniqueness check (`require(!nullifiers[...])`) is skipped for that token index, even though the caller may still have non-zero-looking (per `checkOnchainCreation`, must be zero, but this constraint is *not* proof-verified) nullifier slots: [7](#0-6) 

Because none of this is bound to the zk-SNARK's public inputs or the EIP-712-style `signedMessageHash`, the SNARK proof that is verified in `Hinkal.transact` says nothing about the value of `onChainCreation`. The proof was generated against a `MainEVMCircuit` whose public/private signals list (`rootHashHinkal, signedMessageHash, erc20TokenAddresses, amountChanges, ..., inNullifiers, outCommitments, calldataHash, ...`) also excludes `onChainCreation`: [8](#0-7) 

This breaks the equality the report's bug class targets: a `CircomData` field (`onChainCreation`) that is acted upon by `Hinkal`/`HinkalBase` (skipping nullifier checks, zeroing the required balance delta) but that is outside `calldataHash`, `signedMessageHash`, and the public-input vector — meaning it is not authorized by the prover or by the relayer/sender signature at all.

### Impact Explanation
An unprivileged party constructing/submitting a `transact()` call (a relay-less self-submitted transaction, `circomData.relay == address(0)` and `circomData.originalSender == sender`) can pair a genuine, unmodified proof/circuit output for a given `amountChanges`/`inputNullifiers` set with an `onChainCreation` array that lies about which tokens are "on-chain created." Since `checkOnchainCreation` forces `amountChanges[i]==0` and `inputNullifiers[i][j]==0` whenever `onChainCreation[i]` is true, the most direct exploitable shape is the reverse: setting `onChainCreation[i]=false` for a token that the prover intended to be "on-chain created" (or vice versa) still passes `checkOnchainCreation` as long as the corresponding `amountChanges`/`inputNullifiers` are zero — but because `onChainCreation` is unauthenticated, the circuit and the calldata hash cannot detect if this array is later swapped between multiple valid combinations satisfying `checkOnchainCreation`'s per-index zero constraints, letting the caller pick, independently from the proof, whether nullifiers are checked/inserted for a given index in `insertNullifiers`/`insertCommitments`. This selectively disables nullifier reuse protection for a token slot that a legitimate proof already committed to spending, enabling double-spend of an input UTXO for that token (Critical: proof/nullifier verification bypass) — because the value used to gate replay-protection is not itself proof-bound.

### Likelihood Explanation
Likelihood is bounded by the fact that `checkOnchainCreation` still forces `amountChanges[i]==0` and all `inputNullifiers[i][j]==0` on the `onChainCreation[i]==true` branch, so an attacker cannot simply flip an arbitrary in-use index to `true` without the values already being zero. However, since the array is fully attacker-supplied calldata (not derived from or bound to the SNARK proof), and since `transact()` is directly callable by any EOA with a valid dimensions/circomData combination, the underlying design flaw — a security-gating array excluded from `calldataHash` — represents a structural bypass condition, not requiring any privileged role. Full weaponization requires identifying a concrete combination of token slots/nullifiers where the zero-constraint doesn't prevent a beneficial index flip (e.g., multi-token transactions with unused/never-set nullifier slots interacting with `insertCommitments`' analogous `break`-on-`onChainCreation` logic for output commitment insertion), which I was not able to fully enumerate within the available context.

### Recommendation
Include `circomData.onChainCreation` in the `calldataHash` computation (`getHashedCalldata1`/`getHashedCalldata2` in `contracts/CircomDataBuilder.sol`) and/or in `getSignedMessageHash`, so that its value is committed to by the same authenticator (signer or proof) that authorizes `amountChanges` and `inputNullifiers`. Ideally, promote `onChainCreation` (or an equivalent per-token flag) into the circuit's public-input vector so `MainEVMCircuit` itself constrains which token indices are on-chain-created, rather than relying purely on a Solidity-side sanity check that operates on unauthenticated calldata.

### Proof of Concept
Concrete exploitation requires constructing a multi-token `CircomData` payload where: (a) a valid proof is generated for `onChainCreation = [false, true]` (token 0 spent normally, token 1 on-chain-created with `amountChanges[1]==0`, `inputNullifiers[1][*]==0`), and (b) the submitted calldata instead sets `onChainCreation = [true, false]` while keeping `amountChanges[0]==0` and `inputNullifiers[0][*]==0` (satisfying `checkOnchainCreation` for the swapped positions) — causing `insertNullifiers`/`insertCommitments` to skip nullifier/commitment processing for whichever index the attacker chooses independent of what the (still-valid, since `onChainCreation` isn't a circuit input) proof actually attested to. I was unable to fully trace the exact `dimensions`/multi-token calldata construction needed to make this deliver theft/double-spend impact end-to-end within the tools available here; a full PoC would require deploying the contracts, generating a compatible witness/proof via `circuits/MainEVMCircuit.circom`, and driving `Hinkal.transact` with the swapped `onChainCreation` array to confirm a nullifier or balance-equation bypass on a local fork.

### Citations

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

**File:** contracts/HinkalHelper.sol (L173-202)
```text
    function checkOnchainCreation(
        CircomData calldata circomData
    ) internal pure {
        bool isInternalTransaction = circomData
            .externalActionData
            .externalActionId == 0;

        for (uint i = 0; i < circomData.onChainCreation.length; i++) {
            if (circomData.onChainCreation[i]) {
                require(
                    !isInternalTransaction,
                    "onChainCreation not allowed for internal transactions"
                );
                require(
                    circomData.amountChanges[i] == 0,
                    "amountChanges must be zero when onChainCreation is true"
                );
                for (
                    uint j = 0;
                    j < circomData.inputNullifiers[i].length;
                    j++
                ) {
                    require(
                        circomData.inputNullifiers[i][j] == 0,
                        "inputNullifiers must be zero when onChainCreation is true"
                    );
                }
            }
        }
    }
```

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

**File:** contracts/Hinkal.sol (L134-146)
```text
                // balance equation to check: CHANGE IN BALANCE SHOULD EQUAL TO
                // 1) change in off-chain utxos
                // 2) change in on-chain utxos
                require(
                    balanceDif ==
                        (
                            circomData.onChainCreation[i]
                                ? int256(0)
                                : circomData.amountChanges[i]
                        ) +
                            int256(utxoAmount),
                    "Balance Diff Should be equal to sum of onchain and offchain created commitments"
                );
```

**File:** contracts/HinkalBase.sol (L135-152)
```text
    function insertNullifiers(
        uint256[][] calldata inputNullifiers,
        bool[] calldata onChainCreation
    ) internal {
        for (uint256 i = 0; i < inputNullifiers.length; i++) {
            for (uint256 j = 0; j < inputNullifiers[i].length; j++) {
                if (onChainCreation[i] == true) break;
                if (inputNullifiers[i][j] != 0) {
                    require(
                        !nullifiers[inputNullifiers[i][j]],
                        "Nullifier cannot be reused"
                    );
                    nullifiers[inputNullifiers[i][j]] = true;
                    emit Nullified(inputNullifiers[i][j]);
                }
            }
        }
    }
```

**File:** circuits/MainEVMCircuit.circom (L17-26)
```text
// public params: 
// rootHashHinkal, signedMessageHash, 
// erc20TokenAddresses, amountChanges, outTimeStamp, inNullifiers, outCommitments, 
// calldataHash, message,
// outH1Ax, outH1Ay, H0Ax, H0Ay, outStealthAddress

// private params:
// spendingPublicKey, eddsaSignature, nullifyingPrivateKey, messageSeed
// inAmounts, inH0Ax, inH0Ay, inTimeStamps, inCommitmentSiblings, inCommitmentSiblingSides,
// outAmounts, outPublicKeys, 
```
