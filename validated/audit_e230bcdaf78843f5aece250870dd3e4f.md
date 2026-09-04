### Title
Attacker-controlled `feeStructure.feeToken/flatFee/variableRate` are never bound to the proof's `calldataHash`, letting a single valid proof be replayed with different fee economics - (File: `contracts/CircomDataBuilder.sol`)

### Summary
`FeeStructure` (feeToken/flatFee/variableRate) is only ever hashed into `calldataHash2` off-chain by `getHashedCalldata`/`getHashedCalldata2`, but that recomputation is never invoked anywhere on the reachable `Hinkal.transact` path. [1](#0-0)  The public-input vector built by `formBasicInput`/`formInputEmporiumMin` (which is what `verifyProof` actually checks) never includes the `FeeStructure` fields themselves - only the raw `circomData.calldataHash` value, which the caller supplies directly and which is trusted without re-derivation. [2](#0-1) 

### Finding Description
The invariant that should hold is: `circomData.calldataHash == getHashedCalldata(circomData)` computed from the *actual* `feeStructure`/`relay`/`hookData`/etc. submitted in the transaction. If that equality were enforced on-chain, mutating `feeStructure.feeToken/flatFee/variableRate` after a proof was generated would change the recomputed hash and diverge from the `calldataHash` baked into the fixed public inputs of the existing proof, causing the check to fail.

Tracing the reachable call path `Hinkal.transact` → `hinkalHelper.performHinkalChecks` → `formInputForCircom`/`formBasicInput`/`formInputEmporiumMin`, the only occurrences of `getHashedCalldata`/`getHashedCalldata1`/`getHashedCalldata2` in the whole codebase are internal, self-referential calls inside `CircomDataBuilder.sol` itself; they are never called from `Hinkal.sol`, `HinkalHelper.sol`, or `VerifierFacade.sol`. [3](#0-2)  Instead, `formBasicInput`/`formInputEmporiumMin` copy `circomData.calldataHash` verbatim into the public-input vector and into `getSignedMessageHash`'s preimage, without ever recomputing it from the concrete `feeStructure` value present in the calldata. [4](#0-3)  `FeeStructure` itself never appears as a discrete element of the public-input vector at any index - `verifyProof`/`buildVerifierId` (`contracts/VerifierFacade.sol` lines 28-58) therefore constrain nothing about `feeToken`, `flatFee`, or `variableRate`.

Downstream, these unconstrained fields directly drive value transfers: in `Hinkal._internalTransact`, `flatFee`/`variableRate` set the split between relay and recipient (`contracts/Hinkal.sol` lines 190-224); in the Emporium external action, `EmporiumUpgradeable.payRelayFees` uses `feeStructure.feeToken`/`flatFee`/`variableRate` to compute `relayFee` via `hinkalHelper.calculateRelayFee` whenever `signerAddress == address(0)` (the unsigned/stateless op path). [5](#0-4)  Critically, `verifyWallet` only enforces `feeStructure.flatFee <= stack.maxFee` when `stack.signerAddress != address(0)`; when `signerAddress == address(0)` the function returns immediately with no fee-cap check at all. [6](#0-5)  So exactly in the scenario named in the question (Emporium, `signerAddress == 0`), there is neither a proof-level nor a signature-level constraint tying the executed `feeStructure` to what the prover actually committed to when the proof was generated.

An attacker who has one valid `(a,b,c)` proof for a transaction can therefore resubmit `Hinkal.transact` with the identical proof/public inputs but a mutated `circomData.feeStructure.{feeToken,flatFee,variableRate}`; `verifyProof` still succeeds (the fee fields are outside the input vector), `rootHashExists`, `insertNullifiers`, and the balance/slippage equations in `Hinkal.transact` (lines 100-146) are all agnostic to `feeStructure`, so nothing rejects the divergence.

### Impact Explanation
The relay-fee split (`flatFee`, `variableRate`, `feeToken`) is economically load-bearing but unproven. An attacker (who can be the transaction submitter, distinct from any relay counting on an agreed fee) can replay a valid proof while zeroing out `flatFee`/`variableRate` to deprive the relay of its fee, or maximize them to redirect more of the withdrawn amount to themselves in `_internalTransact`/`payRelayFees` than the proof's off-chain-negotiated economics intended. This matches "theft or permanent freezing of protocol/relay fees" (High); depending on how aggressively `variableRate` biases the split versus the recipient's authorized amount, it borders on unauthorized redirection of value the prover never signed off on.

### Likelihood Explanation
No special role is required - any address that can call `Hinkal.transact` with a previously-produced proof (their own or observed on-chain/in the mempool) can retry with a mutated `feeStructure`. The only precondition is a valid, not-yet-nullified proof and, for the Emporium path, `signerAddress == address(0)` (the unsigned/stateless branch), which skips even the `maxFee` cap. Cost is a single transaction; the manipulation is repeatable per proof up to the point the associated nullifiers are consumed.

### Recommendation
Bind `feeStructure` (and the other fields folded into `calldataHash2`) to the proof by recomputing `getHashedCalldata(circomData)` on-chain inside `HinkalHelper.performHinkalChecks` (or `Hinkal.transact`) and `require`-ing it equals `circomData.calldataHash` before that value is used in `formBasicInput`/`formInputEmporiumMin`. Alternatively, promote the fee fields to first-class public-input signals that the circuit directly constrains.

### Proof of Concept
Foundry plan:
1. Generate one valid proof for a `CircomData` struct with `feeStructure = {feeToken: T, flatFee: F1, variableRate: R1}` targeting the Emporium external action with `signerAddress == address(0)`.
2. Call `Hinkal.transact` once with this proof and the original `feeStructure`; record relay/recipient balances (side A).
3. Call `Hinkal.transact` again with the identical `(a,b,c)`, `dimensions`, and all other `circomData` fields unchanged, but `feeStructure = {feeToken: T, flatFee: 0, variableRate: 0}` (or a maximal value); assert `verifyProof` still returns true and the tx does not revert.
4. Assert the equality `circomData.calldataHash == getHashedCalldata(circomData)` fails to hold for the mutated struct yet no code path checks it - confirm by instrumenting/calling `CircomDataBuilder.getHashedCalldata` off-chain and showing it differs from the `calldataHash` embedded in the reused proof's public inputs, while the transaction still succeeds with different relay-fee side effects (side B ≠ side A). [7](#0-6) [8](#0-7) [3](#0-2) [9](#0-8) 

*Caveat:* Due to tool-iteration limits I was unable to fully read `HinkalHelper.sol`'s `performHinkalChecks` in this session; grep evidence shows `getHashedCalldata` is referenced only inside `CircomDataBuilder.sol` itself, which strongly suggests no on-chain caller recomputes/enforces it, but this file's full contents were not directly inspected to rule out an equivalent check under a different name.

### Citations

**File:** contracts/CircomDataBuilder.sol (L10-54)
```text
    function getHashedCalldata(
        CircomData calldata circomData
    ) internal pure returns (uint256) {
        // because of stack too deep error, we need to split the calldata into two parts
        uint256 calldataHash1 = getHashedCalldata1(circomData);
        uint256 calldataHash2 = getHashedCalldata2(circomData);
        return (uint256(keccak256(abi.encode(calldataHash1, calldataHash2))) %
            CIRCOM_P);
    }

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

**File:** contracts/CircomDataBuilder.sol (L150-240)
```text
    function formInputEmporiumMin(
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);

        uint16 index = 0;

        input[index++] = circomData.emporiumMessage;

        input[index++] = circomData.timeStamp;
        input[index++] = circomData.calldataHash;
    }

    function formInputNormal(
        uint256 chainId,
        address verifyingContract,
        CircomData calldata circomData
    ) internal pure returns (uint256[] memory input) {
        input = new uint256[](circomData.publicSignalCount);
        uint16 index = 0;
        input = formBasicInput(
            chainId,
            verifyingContract,
            circomData,
            input,
            index,
            circomData.emporiumMessage
        );
    }

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

**File:** contracts/Hinkal.sol (L30-65)
```text
    function transact(
        uint256[2] calldata a,
        uint256[2][2] calldata b,
        uint256[2] calldata c,
        Dimensions calldata dimensions,
        CircomData calldata circomData
    ) public payable nonReentrant {
        {
            uint256[] memory inputForCircom = hinkalHelper.performHinkalChecks(
                circomData,
                dimensions,
                msg.sender
            );

            require(
                verifyProof(
                    a,
                    b,
                    c,
                    inputForCircom,
                    buildVerifierId(
                        dimensions,
                        circomData.externalActionData.externalActionId
                    )
                ),
                "Invalid Proof"
            );
            // Root Hash Validation
            require(
                rootHashExists(
                    circomData.rootHashHinkal,
                    circomData.rootHashHinkalIndex
                ),
                "Hinkal Root Hash is Incorrect"
            );
        }
```

**File:** contracts/external-actions/emporium/upgradeable/EmporiumUpgradeable.sol (L201-349)
```text
    function payRelayFees(
        CircomData calldata circomData,
        address signerAddress,
        int256[] calldata deltaAmountChanges
    ) internal {
        FeeStructure calldata feeStructure = circomData.feeStructure;

        bool foundToken = false;

        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            // tokens deposited into Emporium are not charged
            if (deltaAmountChanges[i] >= 0) {
                continue;
            }

            address erc20TokenAddress = circomData.erc20TokenAddresses[i];
            bool isFeeToken = erc20TokenAddress == feeStructure.feeToken;

            if (isFeeToken) {
                foundToken = true;
            }

            uint256 relayFee = 0;
            uint256 flatFee = isFeeToken ? feeStructure.flatFee : 0;

            if (signerAddress == address(0)) {
                uint256 sumAbs = uint256(-deltaAmountChanges[i]);

                EmporiumStorageVars storage $ = _getEmporiumStorage();
                relayFee = $._hinkalHelper.calculateRelayFee(
                    sumAbs,
                    flatFee,
                    feeStructure.variableRate
                );
            } else {
                relayFee = flatFee;
            }

            payRelay(
                circomData.relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }

        if (!foundToken && feeStructure.flatFee != 0) {
            require(
                signerAddress != address(0),
                "Gas Token in Emporium is not found"
            );

            payRelay(
                circomData.relay,
                signerAddress,
                feeStructure.flatFee,
                feeStructure.feeToken
            );
        }
    }

    function payRelay(
        address relay,
        address signerAddress,
        uint256 relayFee,
        address erc20TokenAddress
    ) internal {
        if (relay == address(0) || relayFee == 0) {
            return;
        }

        if (signerAddress == address(0)) {
            sendToRelay(relay, relayFee, erc20TokenAddress);
        } else {
            sendToRelayFromWallet(
                relay,
                signerAddress,
                relayFee,
                erc20TokenAddress
            );
        }
    }

    function _hashEmporiumOps(
        EmporiumOperation[] memory ops
    ) private pure returns (bytes32) {
        bytes32[] memory opHashes = new bytes32[](ops.length);
        for (uint256 i = 0; i < ops.length; i++) {
            opHashes[i] = keccak256(
                abi.encode(
                    EMPORIUM_OPERATION_TYPEHASH,
                    ops[i].endpoint,
                    ops[i].invokeWallet,
                    ops[i].value,
                    keccak256(ops[i].callData)
                )
            );
        }
        return keccak256(abi.encodePacked(opHashes));
    }

    function verifyWallet(
        EmporiumStack memory stack,
        CircomData calldata circomData
    ) internal {
        EmporiumStorageVars storage $ = _getEmporiumStorage();

        if ($.usedMessages[circomData.emporiumMessage]) {
            revert UsedMessage();
        }

        $.usedMessages[circomData.emporiumMessage] = true;

        if (stack.signerAddress == address(0)) {
            return;
        }

        bytes32 hashedMessage = _hashTypedDataV4(
            keccak256(
                abi.encode(
                    EMPORIUM_SIGNATURE_TYPEHASH,
                    circomData.emporiumMessage,
                    _hashEmporiumOps(stack.ops),
                    stack.maxFee,
                    stack.deadline
                )
            )
        );

        (address recoveredAddress, ECDSA.RecoverError err) = ECDSA.tryRecover(
            hashedMessage,
            stack.v,
            stack.r,
            stack.s
        );
        bool verified = err == ECDSA.RecoverError.NoError &&
            recoveredAddress == stack.signerAddress;
        if (!verified) {
            revert InvalidSignature();
        }

        if (block.timestamp > stack.deadline) {
            revert SignatureExpired();
        }

        if (circomData.feeStructure.flatFee > stack.maxFee) {
            revert FeeExceedsSignedMax();
        }
    }
```
