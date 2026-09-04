### Title
Duplicate `erc20TokenAddresses` entries let an attacker mint shielded UTXOs against a single real balance increase - (File: `contracts/Hinkal.sol`)

### Summary
`Hinkal.transact` snapshots balances via `getBalancesForArray(circomData.erc20TokenAddresses)` and then checks, per index `i`, that `balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + utxoAmount`. Neither `Hinkal.sol` nor `HinkalHelper.dimensionsCheck` enforces that entries of `circomData.erc20TokenAddresses` are distinct real assets, so an attacker can register a malicious "mirror" token contract `B` whose `balanceOf` reads the same underlying storage as a real token `A`. A single real transfer of value into Hinkal via `A` then also shows up as a `balanceDif` on `B`, letting the attacker mint a second, unbacked on-chain UTXO for `B` while only one real transfer of tokens occurred.

### Finding Description
The broken equality: real value received by Hinkal (sum of genuine ERC20/ETH transfers) should equal the sum of `amountChanges` (off-chain component) plus the sum of minted on-chain UTXO amounts (`utxoAmount`), across all distinct assets. `Hinkal.transact` instead computes this equality independently per index of `circomData.erc20TokenAddresses` [1](#0-0) , using `getBalancesForArray`, which simply calls `balanceOf`/`address(this).balance` for each address in the caller-supplied array with no de-duplication [2](#0-1) . Neither `dimensionsCheck` nor `checkOnchainCreation` in `HinkalHelper.sol` requires the addresses in `erc20TokenAddresses` to be unique or to represent independent balances [3](#0-2) .

An attacker deploys token `A` (a normal ERC20) and a second contract `B` whose `balanceOf(hinkal)` is wired to read the same storage/mapping as `A` (e.g., a proxy/alias contract that mirrors `A`'s balance for the Hinkal address), while `B.transferFrom`/`transfer` can be implemented as a no-op that still returns `true` (or simply is never invoked because the external action skips a zero-amount transfer for that index). The attacker then calls `Hinkal.transact` with `externalActionId` pointing at `DepositOnChainUtxosExternalAction`, with `erc20TokenAddresses = [A, B]` and `externalActionData.externalActionMetadata` encoding `utxoAmounts = [[100],[100]]`.

Inside `DepositOnChainUtxosExternalAction.runAction`, for index 0 it does a real `transferERC20TokenFrom(A, user, hinkal, 100)`, and for index 1 (token `B`) it also calls `transferERC20TokenFrom(B, user, hinkal, 100)` [4](#0-3) . Because `B`'s `transferFrom` is attacker-controlled, it can be a no-op returning success while `B.balanceOf(hinkal)` mirrors `A`'s real balance change. Back in `Hinkal.transact`, `oldBalances`/`newBalances` are taken for both `A` and `B`; because `B.balanceOf` mirrors `A`'s storage, `balanceDif` for index 1 (`B`) also shows `+100`, even though no real second transfer occurred. The check `balanceDif == amountChanges[i] + utxoAmount` is then satisfied for both indices (with `utxoAmount = 100` matched against the two attacker-crafted UTXOs, one per token address) [5](#0-4) . The result: Hinkal only actually received 100 real tokens (of asset `A`), but two on-chain commitments totaling 200 units of shielded value (100 for `A`, 100 for `B`) are inserted into the tree via `insertCommitments` [6](#0-5) .

None of the existing guards catch this: `performHinkalChecks`/`dimensionsCheck` only checks array-length equality against `dimensions.tokenNumber`, not address uniqueness or real economic independence [7](#0-6) ; `verifyProof` and the circuit only constrain the off-chain UTXO algebra (`inTotal + amountChanges === outTotal`), not the relationship between two independently-chosen token addresses and their real balances, which is purely an on-chain (Solidity) bookkeeping issue; `rootHashExists`, `insertNullifiers`, and `onlyAllowedRecipient` are unrelated to this cross-token balance aliasing.

### Impact Explanation
The attacker can mint shielded UTXO value against `Hinkal` that is not backed 1:1 by real transferred assets, i.e., "minting shielded value without backing" - Critical severity per the rules, since the alias token's minted UTXO for `B` represents claimable value with no corresponding real, redeemable asset ever deposited for `B` specifically. This is repeatable for any amount and any number of duplicate "mirror" addresses the attacker registers, up to `dimensions.tokenNumber` limits, and does not require any privileged role - only deploying attacker-controlled token contracts and calling `transact` with the caller's own funds and proof.

Note: whether the attacker can subsequently *redeem* the phantom `B` UTXO for real value depends on the withdrawal path being able to move real assets out under `B`'s address, which needs further contract design on the attacker's side (e.g., `B.transfer` implemented to actually route real `A` balance controlled by Hinkal). This part is not fully traced/validated here, so the "protocolwide insolvency realized via withdrawal" leg of the attack is not confirmed; what is confirmed is that the accounting invariant checked by `Hinkal.transact` can be violated (unbacked UTXO minted) via duplicate/aliased `erc20TokenAddresses` entries.

### Likelihood Explanation
Preconditions: attacker must deploy a custom "mirror" token contract whose `balanceOf` for the Hinkal address is linked to another token's storage, and must route both addresses through the `erc20TokenAddresses` array of a single `transact` call with a compatible external action (e.g. `DepositOnChainUtxosExternalAction`, which performs a `transferFrom` per index and creates a UTXO per index using attacker-supplied amounts). This is fully within an unprivileged attacker's control (they can deploy arbitrary contracts and control all `CircomData` fields for their own deposit). Feasibility is high given no on-chain uniqueness check exists on `erc20TokenAddresses`; the primary remaining engineering work for the attacker is building the mirrored-balance token, which is straightforward Solidity.

### Recommendation
Enforce uniqueness of `circomData.erc20TokenAddresses` entries in `HinkalHelper.dimensionsCheck` (or in `Hinkal.transact` before taking balance snapshots), rejecting any transaction where the same address appears twice. Additionally, consider hardening the balance-diff accounting to be based on a single global before/after snapshot keyed by canonical token identity, and audit any external actions (e.g. `DepositOnChainUtxosExternalAction`) to ensure the same address cannot be double-counted for both a real transfer and a phantom UTXO of a different address whose balance happens to move in lockstep. A stricter fix is to have external actions and `transact` independently attribute exactly one real transfer to exactly one UTXO amount, not rely purely on `balanceOf` deltas over an attacker-chosen address list.

### Proof of Concept
Foundry test plan:
1. Deploy real ERC20 `TokenA`.
2. Deploy `MirrorTokenB` whose `balanceOf(address who)` returns `TokenA.balanceOf(who)`, and whose `transferFrom`/`transfer` are no-ops returning `true`.
3. Fund attacker with 100 `TokenA`, approve Hinkal/`DepositOnChainUtxosExternalAction`.
4. Craft valid `CircomData`/proof (locally generated) with `erc20TokenAddresses = [TokenA, MirrorTokenB]`, `externalActionData` pointing to `DepositOnChainUtxosExternalAction`, `externalActionMetadata` encoding `utxoAmounts = [[100],[100]]`, `amountChanges = [0,0]`, `onChainCreation = [true,true]`, `slippageValues = [0,0]`.
5. Call `Hinkal.transact(...)`.
6. Assert: `TokenA.balanceOf(hinkal) == 100` (real vault balance increase) while two `NewCommitment` events / on-chain UTXOs are emitted totaling 200 units of shielded value (one UTXO of 100 for `TokenA`, one UTXO of 100 for `MirrorTokenB`) - i.e. assert `sum(mintedUtxoAmounts) (200) > realTokenBalanceDelta (100)`, violating "net tokens entering Hinkal == sum(amountChanges) + sum(minted UTXO amounts)".

### Citations

**File:** contracts/Hinkal.sol (L78-146)
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
```

**File:** contracts/Hinkal.sol (L156-167)
```text
            insertNullifiers(
                circomData.inputNullifiers,
                circomData.onChainCreation
            );

            insertCommitments(
                circomData.outCommitments,
                circomData.encryptedOutputs,
                onChainCommitments,
                circomData.onChainCreation
            );
        }
```

**File:** contracts/Transferer.sol (L169-176)
```text
    function getBalancesForArray(
        address[] calldata erc20TokenAddresses
    ) internal view returns (uint256[] memory balances) {
        balances = new uint256[](erc20TokenAddresses.length);
        for (uint64 i; i < erc20TokenAddresses.length; i++) {
            balances[i] = getERC20OrETHBalance(erc20TokenAddresses[i]);
        }
    }
```

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

**File:** contracts/external-actions/DepositOnChainUtxosExternalAction.sol (L49-83)
```text
        for (uint256 i = 0; i < tokenCount; i++) {
            require(
                deltaAmounts[i] == 0,
                "DepositOnChainUtxosExternalAction: Delta amount must be zero"
            );

            address tokenAddress = circomData.erc20TokenAddresses[i];
            uint256 tokenTotal = 0;

            for (uint256 j = 0; j < utxoAmounts[i].length; j++) {
                uint256 amount = utxoAmounts[i][j];
                require(
                    amount > 0,
                    "DepositOnChainUtxosExternalAction: UTXO amount must be positive"
                );
                tokenTotal += amount;

                utxoSet[utxoIndex] = UTXO({
                    amount: amount,
                    erc20Address: tokenAddress,
                    stealthAddressStructure: circomData.stealthAddressStructure,
                    timeStamp: circomData.timeStamp + utxoIndex
                });
                utxoIndex++;
            }

            if (tokenAddress != address(0) && tokenTotal > 0) {
                transferERC20TokenFrom(
                    tokenAddress,
                    userAddress,
                    msg.sender,
                    tokenTotal
                );
            }
        }
```
