### Title
Duplicate token-address indices in `erc20TokenAddresses` cause on-chain UTXO commitments to be double-inserted, minting shielded value without backing - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact` never enforces that `circomData.erc20TokenAddresses` entries are unique, and its per-index accounting loop re-scans the *entire* `utxoSet` returned by an external action for every index whose address matches. By repeating the same token address at two indices — one with `onChainCreation=false, amountChanges=0` and one with `onChainCreation=true` — an attacker can make the same real UTXO get pushed into `onChainCommitments` twice, so it is inserted as **two independent, separately-spendable merkle leaves** while only being backed by a single real deposit.

### Finding Description
The equality that should hold is: *for a given token X, the total value represented by leaves inserted into the tree via `onChainCommitments` must equal the total value actually contained in the `utxoSet` returned once by the external action for token X, which itself must equal the real, one-time balance increase (`balanceDif`) for that token.*

In `Hinkal.transact` (contracts/Hinkal.sol), the accounting loop is: [1](#0-0) 

For each index `i` in `circomData.erc20TokenAddresses`, an inner loop iterates over the *entire* `utxoSet` and, for every entry whose address matches `erc20TokenAddresses[i]`, both sums `utxoAmount` and unconditionally appends a fresh `OnChainCommitment` to `onChainCommitments`, incrementing `onChainCommitmentCounter`: [2](#0-1) 

Nothing marks a `utxoSet[j]` entry as "already consumed" by a previous index. If the attacker supplies `erc20TokenAddresses = [X, X]` with a single UTXO of amount `M` for token `X` in `utxoSet` (produced legitimately by any already-registered `IExternalActionV2`, e.g. `DepositOnChainUtxosExternalAction`, backed by a real transfer of `M` tokens into Hinkal), then:
- At `i=0`: `utxoAmount = M`, one `OnChainCommitment` for the UTXO is appended.
- At `i=1` (same address `X`): the loop matches the *same* UTXO again, `utxoAmount = M` again, and a **second, identical** `OnChainCommitment` is appended.

The balance-equation check is satisfied simultaneously for both indices because `balanceDif` (the real, single measured balance change of `M`) is compared independently per index against `(onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount`:
- `i=0`, `onChainCreation[0]=false`, `amountChanges[0]=0` → `M == 0 + M` ✓
- `i=1`, `onChainCreation[1]=true` (forces `amountChanges[1]=0` and empty `inputNullifiers[1]` per `checkOnchainCreation`) → `M == 0 + M` ✓ [3](#0-2) 

`checkOnchainCreation` and `dimensionsCheck` never check that `erc20TokenAddresses` entries are distinct: [4](#0-3) 

Nor does `MainEVMCircuit.circom`/`CircomDataBuilder.formInputForCircom` reference `onChainCreation` or enforce address uniqueness — `onChainCreation` is a pure Solidity bookkeeping flag folded only into `calldataHash`, so the circuit places no constraint preventing this. `insertCommitments` then blindly inserts both (identical) commitments as two separate merkle leaves: [5](#0-4) 

The net result: two independent, separately redeemable shielded UTXOs of value `M` each (`2M` total) are created in the merkle tree while only `M` tokens were ever actually deposited into Hinkal — value minted without backing.

### Impact Explanation
An unprivileged attacker who deposits `M` tokens via any legitimate registered external action can walk away with `2M` (or more, by adding further duplicate indices) of spendable shielded balance after later spending both resulting UTXOs through normal `transact` calls with valid nullifiers/proofs for their own leaves. This is a direct protocol-insolvency mint: Critical severity ("minting shielded value without backing"), fully repeatable per transaction and scalable by adding more duplicate token-address slots in a single call.

### Likelihood Explanation
No privileged role is required. The attacker only needs: (1) an existing registered `externalActionId` (already-deployed actions like `DepositOnChainUtxosExternalAction` suffice), (2) the ability to craft `CircomData` with duplicate entries in `erc20TokenAddresses`, matching `onChainCreation`/`amountChanges`/`inputNullifiers` arrays satisfying `checkOnchainCreation`, and (3) a self-generated valid ZK proof for those public inputs (attacker controls their own proof generation). No race condition or timing dependency is needed; the exploit is deterministic and cost is limited to gas plus the single real deposit `M`.

### Recommendation
Enforce uniqueness of `erc20TokenAddresses` in `dimensionsCheck`/`checkOnchainCreation` (reject duplicate addresses), or restructure the `utxoAmount`/`onChainCommitments` loop in `Hinkal.transact` to mark each `utxoSet[j]` as consumed once matched to an index (e.g., track a `bool[] consumed` and skip already-matched entries), so a single returned UTXO can only ever be attributed and inserted once regardless of how many times its token address appears in `erc20TokenAddresses`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, register `DepositOnChainUtxosExternalAction` (or reuse existing test fixture) with `externalActionId`.
2. Attacker calls `transact` with `circomData.erc20TokenAddresses = [tokenX, tokenX]`, `onChainCreation = [false, true]`, `amountChanges = [0, 0]`, `inputNullifiers` all zero, `externalActionData` pointing at the registered action, and craft the external action call so it returns a single `utxoSet` entry for `tokenX` of amount `M`, backed by a real transfer of `M` `tokenX` from attacker.
3. Generate a valid proof locally for this `CircomData`/`Dimensions` (satisfiable since `amountChanges` are both zero and nullifiers are empty).
4. Assert before/after: `hinkal.balanceOf(tokenX)` increases by exactly `M` (real backing), while `NewCommitment` events / merkle tree insertions show **two** leaves at the on-chain UTXO's commitment value (assert `onChainCommitmentCounter`-derived leaves == 2, or track emitted `NewCommitment` events count for on-chain creation == 2).
5. Redeem both leaves via subsequent `transact` calls with correct nullifiers/proofs; assert attacker extracts `2M` total value from the contract, exceeding the single `M` real deposit — confirming minted value exceeds backing (violates `sum(inserted on-chain leaf values for token X) == sum(utxoSet value for token X == real balanceDif)`).

### Citations

**File:** contracts/Hinkal.sol (L97-147)
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

**File:** contracts/HinkalBase.sol (L100-105)
```text
            for (uint256 i = 0; i < onChainCommitments.length; i++) {
                leaves[index++] = onChainCommitments[i].commitment;
            }

            // 3) Inserting Leaves
            uint256[] memory insertedIndexes = insertMany(leaves);
```
