This confirms the finding is valid.

### Title
On-chain UTXO `timeStamp` is fully attacker-controlled with no bound to `block.timestamp` - ([File: contracts/HinkalHelper.sol])

### Summary
`performHinkalChecks` (via `dimensionsCheck` and `checkOnchainCreation`) never validates `circomData.timeStamp` against `block.timestamp`, and the circuit only hashes it into the public-signal vector without any range/staleness constraint. When `onChainCreation[i]=true`, `DepositOnChainUtxosExternalAction.runAction` uses `circomData.timeStamp + utxoIndex` directly as the stored `UTXO.timeStamp`, which becomes part of `OnChainCommitment.commitment` and the leaf inserted into the Merkle tree via `createOnchainCommitment`.

### Finding Description
The broken equality: `OnChainCommitment.utxo.timeStamp` is expected (by relays/indexers for UTXO discovery/ordering) to approximate `block.timestamp` at creation, i.e. `utxo.timeStamp ≈ block.timestamp`. No code enforces this. [1](#0-0)  `dimensionsCheck` and `checkOnchainCreation` validate array lengths and that `amountChanges`/`inputNullifiers` are zero for on-chain-created entries, but never touch `timeStamp`.

`circomData.timeStamp` is hashed into the signed-message hash and public input vector [2](#0-1) [3](#0-2) , satisfying "proof coverage" trivially — the circuit just needs the caller-supplied value to be consistent, it never checks it against any real-time oracle.

For deposits into on-chain UTXOs, `DepositOnChainUtxosExternalAction.runAction` explicitly builds `UTXO.timeStamp: circomData.timeStamp + utxoIndex` — fully attacker-supplied — as documented in its own comment ("their timestamps come from `circomData.timeStamp` rather than from the block"). [4](#0-3) [5](#0-4) 

This `UTXO` struct flows unchanged into `createOnchainCommitment`, which hashes `utxo.timeStamp` into the stored `commitment` leaf and emits it in `NewCommitment` [6](#0-5) . Neither `insertNullifiers`, `insertCommitments`, `rootHashExists`, nor the balance/slippage checks in `Hinkal.transact` compare `timeStamp` to `block.timestamp` anywhere [7](#0-6) .

Attacker flow: call `Hinkal.transact` with `externalActionData.externalActionId` set to the `DepositOnChainUtxosExternalAction` id, `onChainCreation[i]=true`, `amountChanges[i]=0`, `inputNullifiers[i][*]=0` (satisfying `checkOnchainCreation`), and `circomData.timeStamp = type(uint256).max` (or `0`). Generate a valid proof over these self-chosen public inputs (the attacker fully controls all `CircomData` fields per the threat model), pay the real token amount via `utxoAmounts` metadata, and the transaction succeeds, storing a `OnChainCommitment` with an arbitrary timestamp.

### Impact Explanation
No funds are stolen or double-spent — the balance and amount checks in `Hinkal.transact` (`balanceDif == ... + utxoAmount`) still correctly account for value moved, and nullifiers are unaffected for on-chain-created UTXOs. The impact is limited to metadata integrity: off-chain indexers/relays that use `UTXO.timeStamp` for discovery ordering, fee-timing logic, or "freshness" heuristics can be misled into misordering or mis-scheduling discovery of a legitimate, correctly-funded UTXO. This matches the "temporary freezing/misordering of user funds discovery" characterization — it is the attacker's own UTXO being manipulated, not another user's, since `originalSender`/`userAddress` must equal the depositor for `DepositOnChainUtxosExternalAction` to run.

### Likelihood Explanation
Trivial and repeatable: the attacker needs no privileged role, just the ability to deposit their own funds and generate a locally-computed valid proof for their own chosen public inputs (in-scope per the threat model). Every `transact()` call with `onChainCreation[i]=true` can set an arbitrary `timeStamp`.

### Recommendation
Add a bound in `HinkalHelper` (e.g., in `checkOnchainCreation` or a new check within `performHinkalChecks`) requiring `circomData.timeStamp` to be within an acceptable window of `block.timestamp` (e.g., `block.timestamp - MAX_PAST <= circomData.timeStamp <= block.timestamp + MAX_FUTURE`), or simply overwrite `utxo.timeStamp` with `block.timestamp` inside `DepositOnChainUtxosExternalAction.runAction` / `createOnchainCommitment` rather than trusting caller input, consistent with how `_createProoflessDepositCommitments` already correctly uses `block.timestamp` for proofless deposits. [8](#0-7) 

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, and `DepositOnChainUtxosExternalAction`; register the action id.
2. Build `circomData` with `onChainCreation = [true]`, `amountChanges = [0]`, `inputNullifiers = [[0]]`, `externalActionData.externalActionMetadata = abi.encode([[amount]])`, and `circomData.timeStamp = type(uint256).max`.
3. Generate a valid Groth16 proof locally over the resulting public inputs (attacker-controlled, self-consistent).
4. Call `transact(a,b,c,dimensions,circomData)` from the attacker EOA with the correct token approval/transfer.
5. Assert the call succeeds (`verifyProof` returns true, balance/slippage checks pass).
6. Decode the emitted `NewCommitment` event / query `hinkalHelper`/`Hinkal` state to confirm the stored `OnChainCommitment.utxo.timeStamp == type(uint256).max` while `block.timestamp` remains a normal chain value.
7. Assert no subsequent Merkle insert (`insertMany`) or nullifier check (`insertNullifiers`) reverts, confirming the state divergence (`utxo.timeStamp` vs. `block.timestamp`) persists unguarded on-chain.

### Citations

**File:** contracts/HinkalHelper.sol (L64-202)
```text
    function dimensionsCheck(
        CircomData calldata circomData,
        Dimensions calldata dimensions
    ) internal pure {
        require(
            circomData.erc20TokenAddresses.length == dimensions.tokenNumber,
            "erc20TokenAddresses number should be equal to token number"
        );
        require(
            circomData.amountChanges.length == dimensions.tokenNumber,
            "AmountChanges number should be equal to token number"
        );

        require(
            circomData.onChainCreation.length == dimensions.tokenNumber,
            "onchain creation is equal to tokens count"
        );

        require(
            circomData.slippageValues.length == dimensions.tokenNumber,
            "slippageValues length should be equal to tokens count"
        );

        require(
            circomData.inputNullifiers.length == dimensions.tokenNumber,
            "InputNullifiers number should be equal to token number"
        );

        uint previousNullifierAmount = circomData.inputNullifiers.length > 0
            ? circomData.inputNullifiers[0].length
            : 0;
        for (uint i = 1; i < circomData.inputNullifiers.length; i++) {
            require(
                circomData.inputNullifiers[i].length == previousNullifierAmount,
                "Nullifier amount should be equal"
            );
        }
        require(
            previousNullifierAmount == dimensions.nullifierAmount,
            "Actual and Claimed Nullifier Amount should be equal"
        );

        require(
            circomData.outCommitments.length == dimensions.tokenNumber,
            "OutCommitments number should be equal to token number"
        );

        uint previousCommitmentAmount = circomData.outCommitments.length > 0
            ? circomData.outCommitments[0].length
            : 0;

        for (uint i = 1; i < circomData.outCommitments.length; i++) {
            require(
                circomData.outCommitments[i].length == previousCommitmentAmount,
                "Commitment amount should be equal"
            );
        }
        require(
            previousCommitmentAmount == dimensions.outputAmount,
            "Actual and Claimed Commitment Amount should be equal"
        );

        require(
            circomData.encryptedOutputs.length == dimensions.tokenNumber,
            "EncryptedOutputs number should be equal to token number"
        );

        uint previousEncryptedOutputAmount = circomData
            .encryptedOutputs
            .length > 0
            ? circomData.encryptedOutputs[0].length
            : 0;

        for (uint i = 0; i < circomData.encryptedOutputs.length; i++) {
            require(
                circomData.encryptedOutputs[i].length ==
                    previousEncryptedOutputAmount,
                "Encrypted output amount should be equal"
            );

            for (uint j = 0; j < circomData.encryptedOutputs[i].length; j++) {
                require(
                    circomData.encryptedOutputs[i][j].length > 0,
                    "Missing encrypted output for off-chain commitment"
                );
            }
        }

        require(
            previousEncryptedOutputAmount == dimensions.outputAmount,
            "Actual and Claimed Encrypted Output Amount should be equal"
        );

        require(
            circomData.onChainEncryptedOutput.length > 0,
            "Missing encrypted output for on-chain commitment"
        );

        require(
            circomData.stealthAddressStructure.H0x != 0,
            "H0x cannot be zero"
        );

        require(
            circomData.feeStructure.variableRate <= 10000,
            "Variable rate cannot be greater than 10000"
        );
    }

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

**File:** contracts/CircomDataBuilder.sol (L104-119)
```text
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
```

**File:** contracts/CircomDataBuilder.sol (L227-227)
```text
        input[index++] = circomData.timeStamp;
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L10-13)
```text
/// @title DepositOnChainUtxosExternalAction
/// @notice Deposits tokens into Hinkal and creates on-chain UTXOs whose commitments
/// are fully determined by the caller, because their timestamps come from
/// circomData.timeStamp rather than from the block.
```

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L66-72)
```text
                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
```

**File:** contracts/HinkalBase.sol (L53-70)
```text
    function createOnchainCommitment(
        UTXO memory utxo,
        bytes calldata onChainEncryptedOutput
    ) internal view returns (OnChainCommitment memory) {
        uint256 commitment = hash4(
            utxo.amount,
            uint256(uint160(utxo.erc20Address)),
            utxo.stealthAddressStructure.stealthAddress,
            utxo.timeStamp
        );

        OnChainCommitment memory onChainCommitment = OnChainCommitment({
            utxo: utxo,
            commitment: commitment,
            onChainEncryptedOutput: onChainEncryptedOutput
        });
        return onChainCommitment;
    }
```

**File:** contracts/Hinkal.sol (L92-147)
```text
            OnChainCommitment[]
                memory onChainCommitments = new OnChainCommitment[](
                    utxoSet.length
                );
            uint256 onChainCommitmentCounter = 0;
            for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
                int256 balanceDif;

                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
                } else {
                    balanceDif =
                        int256(newBalances[i]) -
                        int256(oldBalances[i]);
                }
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
                );

                uint256 utxoAmount = 0;
                for (uint j = 0; j < utxoSet.length; j++) {
                    if (
                        utxoSet[j].erc20Address ==
                        circomData.erc20TokenAddresses[i]
                    ) {
                        utxoAmount += utxoSet[j].amount;

                        onChainCommitments[
                            onChainCommitmentCounter
                        ] = createOnchainCommitment(
                            utxoSet[j],
                            circomData.onChainEncryptedOutput
                        );
                        onChainCommitmentCounter++;
                    }
                }

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
            }
```

**File:** contracts/Hinkal.sol (L336-346)
```text
        for (uint256 i = 0; i < length; i++) {
            onChainCommitmentsArray[i] = createOnchainCommitment(
                UTXO({
                    amount: amounts[i],
                    erc20Address: erc20Addresses[i],
                    stealthAddressStructure: stealthAddressStructures[i],
                    timeStamp: block.timestamp
                }),
                onChainEncryptedOutputs[i]
            );
        }
```
