### Title
Duplicate `erc20TokenAddresses` entries allow re-matching the same on-chain UTXO into multiple `OnChainCommitment` leaves, minting unbacked shielded value - (File: contracts/Hinkal.sol)

### Summary
The `onChainCommitments` construction loop in `transact` re-scans the full `utxoSet` for every entry of `circomData.erc20TokenAddresses` without marking already-matched UTXOs as consumed, and no upstream check (`dimensionsCheck`, `checkOnchainCreation`, `performHinkalChecks`) rejects duplicate token addresses. A duplicated token entry causes the same physical on-chain UTXO to be turned into two identical `OnChainCommitment` leaves while only one unit of value actually entered the contract.

### Finding Description
The broken equality: total committed on-chain UTXO value inserted into the Merkle tree (`2A`) should equal the real token amount that moved into `Hinkal` (`A`), but the code allows `2A` to be recorded for `A` actually transferred.

Trace:
- `oldBalances`/`newBalances` are fetched once for the whole `erc20TokenAddresses` array via `getBalancesForArray` [1](#0-0) . If `erc20TokenAddresses` contains `TOKEN_X` twice, both array positions read the identical balance snapshot, so `balanceDif` computed at `i=0` and `i=1` for `TOKEN_X` is numerically identical (both equal the single real transferred amount `A`) [2](#0-1) .
- No uniqueness constraint on `erc20TokenAddresses` exists in `dimensionsCheck` or `checkOnchainCreation` in `HinkalHelper.sol` — these only check array-length equality across parallel arrays and zero out `amountChanges`/`inputNullifiers` for `onChainCreation` entries, never checking for duplicate token addresses [3](#0-2) [4](#0-3) .
- The inner loop `for (uint j = 0; j < utxoSet.length; j++)` matches by `erc20Address` alone and has no "already consumed" tracking; it executes independently for every outer index `i`, so the SAME `utxoSet[j]` element is matched, added into `utxoAmount`, and passed to `createOnchainCommitment` again for each duplicate `i` [5](#0-4) .
- The `require(balanceDif == ... + int256(utxoAmount))` check is evaluated independently per outer index `i`, not cumulatively across all indices for the same token, so it passes identically twice using the same real `A` on both sides [6](#0-5) .
- `createOnchainCommitment` hashes only `utxo.amount`, `erc20Address`, `stealthAddress`, `timeStamp` — since the matched `utxoSet[j]` element is identical both times, the two `OnChainCommitment`s produced are byte-for-byte identical, including the resulting `commitment` hash [7](#0-6) .
- `insertCommitments` inserts both identical commitments as two separate leaves at two separate tree positions via `insertMany`, each emitting its own `NewCommitment` event with a distinct `insertedIndexes` value [8](#0-7) .

Root cause: (1) no dedup/uniqueness enforcement on `circomData.erc20TokenAddresses` anywhere upstream, and (2) the utxoSet-matching inner loop has no per-element "consumed" guard, so a duplicated token index can re-claim the same UTXO as if it were newly created on-chain value again.

### Impact Explanation
If a spender can later prove ownership of both resulting leaves independently (which depends on whether the circuit's nullifier derivation binds to the leaf's tree position/index in addition to the commitment secret — a detail governed by `circuits/MainEVMCircuit.circom`, which I was not able to fully verify within this session), this becomes a direct minting-without-backing / double-spend of shielded value, matching the Critical severity category (minting shielded value without backing, direct theft/insolvency). Even absent full circuit confirmation, the on-chain bookkeeping alone permanently records `2A` of committed on-chain UTXO value against only `A` of actual token custody, which is an accounting/insolvency defect at the `Hinkal.sol` layer regardless of whether both leaves are separately spendable.

### Likelihood Explanation
The attacker only needs to be an unprivileged EOA who can craft `CircomData` with a duplicated `erc20TokenAddresses` entry, matching `onChainCreation` flags, and a proof for their own genuine UTXO set from any external action that returns exactly one UTXO for `TOKEN_X`. No privileged role is required. The main uncertainty is whether the circuit's public-input binding (`formInputForCircom` / `MainEVMCircuit.circom`) independently constrains `erc20TokenAddresses` to be distinct per index or ties the on-chain UTXO count to a circuit-enforced value — this circuit-side constraint could not be fully verified in the available tool budget, so likelihood is stated as plausible but not fully confirmed end-to-end.

### Recommendation
Enforce uniqueness of `circomData.erc20TokenAddresses` in `dimensionsCheck` or `checkOnchainCreation` (reject duplicate entries), and additionally add a "consumed" boolean array over `utxoSet` in the `onChainCommitments` construction loop in `contracts/Hinkal.sol` so each `utxoSet[j]` can only be matched and committed once across the whole outer loop, regardless of duplicate token addresses.

### Proof of Concept
Not fully executable within this session — would require: a Foundry/Hardhat test that (1) deploys a mock external action returning one `UTXO` of amount `A` for `TOKEN_X`, (2) calls `transact` with `erc20TokenAddresses = [TOKEN_X, TOKEN_X]`, matching `onChainCreation = [true, true]`, `amountChanges = [0, 0]`, `slippageValues` set to allow `balanceDif == A`, with a real (or mocked) verifier accepting the proof, (3) asserts `onChainCommitmentCounter == 2` and two `NewCommitment` events / Merkle leaves are inserted for a single `A` transferred, and (4) attempts to prove/spend the second leaf to confirm double-spendability via the circuit's nullifier scheme. This last step depends on `circuits/MainEVMCircuit.circom` internals not fully inspected in this session.

### Citations

**File:** contracts/Hinkal.sol (L78-90)
```text
            uint256[] memory oldBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );

            if (circomData.externalActionData.externalActionId == 0) {
                _internalTransact(circomData);
            } else {
                utxoSet = _externalTransact(circomData);
            }

            uint256[] memory newBalances = getBalancesForArray(
                circomData.erc20TokenAddresses
            );
```

**File:** contracts/Hinkal.sol (L97-114)
```text
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
```

**File:** contracts/Hinkal.sol (L116-132)
```text
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

**File:** contracts/HinkalHelper.sol (L64-171)
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

**File:** contracts/HinkalBase.sol (L72-133)
```text
    function insertCommitments(
        uint256[][] memory offChainCommitments,
        bytes[][] memory offChainEncryptedOutputs,
        OnChainCommitment[] memory onChainCommitments,
        bool[] memory onChainCreation
    ) internal {
        // 1) Total Length of Commitments
        uint256 length = 0;
        for (uint256 i = 0; i < offChainCommitments.length; i++) {
            for (uint256 j = 0; j < offChainCommitments[i].length; j++) {
                if (onChainCreation[i]) break;
                length += offChainCommitments[i][j] != 0 ? 1 : 0;
            }
        }
        length += onChainCommitments.length;

        if (length > 0) {
            // 2) Flattening leaves array
            uint256[] memory leaves = new uint256[](length);
            uint256 index = 0;
            for (uint256 i = 0; i < offChainCommitments.length; i++) {
                for (uint256 j = 0; j < offChainCommitments[i].length; j++) {
                    if (onChainCreation[i] == true) break;
                    if (offChainCommitments[i][j] != 0) {
                        leaves[index++] = offChainCommitments[i][j];
                    }
                }
            }
            for (uint256 i = 0; i < onChainCommitments.length; i++) {
                leaves[index++] = onChainCommitments[i].commitment;
            }

            // 3) Inserting Leaves
            uint256[] memory insertedIndexes = insertMany(leaves);

            // 4) Emitting Commitments/EncryptedOutputs
            index = 0;
            for (uint256 i = 0; i < offChainEncryptedOutputs.length; i++) {
                for (uint256 j = 0; j < offChainEncryptedOutputs[i].length; j++) {
                    if (onChainCreation[i] == true) break;
                    if (offChainCommitments[i][j] != 0) {
                        emit NewCommitment(
                            leaves[index],
                            int256(insertedIndexes[index]),
                            offChainEncryptedOutputs[i][j]
                        );
                        index++;
                    }
                }
            }
            for (uint256 i = 0; i < onChainCommitments.length; i++) {
                emit NewCommitment(
                    leaves[index],
                    -1 * int256(insertedIndexes[index++]),
                    abi.encode(
                        onChainCommitments[i].utxo,
                        onChainCommitments[i].onChainEncryptedOutput
                    )
                );
            }
        }
    }
```
