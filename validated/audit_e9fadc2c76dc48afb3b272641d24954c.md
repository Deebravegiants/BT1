### Title
`msg.value` double-counted when `address(0)` is repeated in `erc20TokenAddresses`, allowing one ETH deposit to back two independent shielded-value credits - (`contracts/Hinkal.sol :: transact`)

### Summary
`Hinkal.transact` iterates `circomData.erc20TokenAddresses` without deduplication and re-applies the full `msg.value` correction to every slot whose address is `address(0)`. Because the per-token balance check `balanceDif == amountChanges[i] + utxoAmount` is evaluated independently per array index rather than per unique token, an attacker can list `address(0)` twice and cause a single real ETH deposit to simultaneously satisfy two separate slot equations, letting the accompanying ZK proof mint shielded value twice for one deposit.

### Finding Description
**Broken equality:** the protocol's intended invariant is
`msg.value backing == exactly one accounting term (amountChanges[i] + utxoAmount for token i)` summed over unique tokens.

In `Hinkal.sol`:
```
for (uint64 i; i < circomData.erc20TokenAddresses.length; i++) {
    ...
    if (circomData.erc20TokenAddresses[i] == address(0)) {
        balanceDif = int256(newBalances[i]) + int256(msg.value) - int256(oldBalances[i]);
    } ...
    require(balanceDif == (onChainCreation[i] ? 0 : amountChanges[i]) + int256(utxoAmount), ...);
}
``` [1](#0-0) 

`oldBalances`/`newBalances` are snapshots of `address(this).balance` taken once, before/after the whole action (`getBalancesForArray` at lines 78 and 88) [2](#0-1) . Since `msg.value` is credited to `address(this).balance` atomically when the payable call is entered, it is already folded into `oldBalances`; the `+ msg.value` term exists to correct for that for a *single* ETH slot. If `address(0)` appears at two indices `i0` and `i1`, both indices read the identical `oldBalances[i]`/`newBalances[i]` and therefore compute the identical `balanceDif` — but that same physical `msg.value` correction is applied, and independently checked, against `amountChanges[i0]` and `amountChanges[i1]` separately.

Nothing in the reachable path deduplicates `erc20TokenAddresses`. `dimensionsCheck` in `HinkalHelper.sol` only validates array lengths against `dimensions.tokenNumber`, never distinctness of the addresses [3](#0-2) . `performHinkalChecks` calls only `relayerIsValid`, `dimensionsCheck`, and `checkOnchainCreation` — none of which reject duplicate token entries [4](#0-3) .

The circuit constraint `inTotal[i] + amountChanges[i] === outTotal[i]` is enforced per public-input slot `i`, not per unique token address, so the proof happily accepts two independent slots each claiming `amountChanges = V` for token `address(0)`, as long as the prover's own UTXO tree bookkeeping is internally consistent for each slot. Because the on-chain check treats both slots as separately backed by the same `msg.value`, the attacker satisfies both `require`s with only one real ETH deposit `V`, while the circuit lets both slots independently create output UTXOs/commitments summing to more shielded value than was deposited.

Concretely: attacker sets `erc20TokenAddresses = [address(0), address(0), ...]`, sends `msg.value = V`, sets `amountChanges[0] = V`, `amountChanges[1] = V`, `onChainCreation` false for both, and arranges (via `EmporiumUpgradeable.runAction`, e.g., a no-op operation list) that no extra on-chain UTXO is produced (`utxoAmount = 0` for both slots). Both `require` checks at lines 137-146 pass because `balanceDif` for both slots equals `V` and `amountChanges[i] = V` for each — yet only one `V` of real ETH ever entered the contract. The off-chain circuit is satisfied because, per slot, `inTotal[i] + V === outTotal[i]`, so the prover can mint `2V` of shielded output value from `1V` real backing.

`ExternalActionBaseV2`/`onlyAllowedRecipient`, `verifyProof`, `rootHashExists`, `insertNullifiers`, and `nonReentrant` all operate correctly but never check for duplicate tokens in `circomData.erc20TokenAddresses`, so none of them block this. The post-hook (`afterTransact`) executing between the balance check and `insertNullifiers`/`insertCommitments` [5](#0-4)  is not required to trigger this bug — the double count is already complete purely from the duplicate-array-index processing, independent of any hook.

### Impact Explanation
The attacker can mint shielded value (ETH UTXOs / balance credit) with no matching real backing, directly causing protocol insolvency — the shielded ledger's total claimed ETH exceeds `address(this).balance`. This matches the "Critical — minting shielded value without backing" category. The attack is repeatable for any number of duplicated `address(0)` entries per transaction, scaling the unbacked mint amount, and requires no privileged role — only the ability to craft `CircomData` and produce a proof over attacker-chosen private witness values.

### Likelihood Explanation
Preconditions: attacker only needs to be able to call `Hinkal.transact` with a self-generated proof for an external action registered at `externalActionMap` (e.g. `EmporiumUpgradeable`), listing `address(0)` twice in `erc20TokenAddresses`, and controlling `amountChanges`/`onChainCreation` for both slots. No special tree state, no relay/owner role, no hook contract is strictly necessary. The cost is one deposit of `V` ETH; the gain is up to `V` in unbacked shielded credit per duplicated slot. This is straightforward to construct and repeatable.

### Recommendation
Enforce uniqueness of `erc20TokenAddresses` in `dimensionsCheck` (or a dedicated check in `performHinkalChecks`), rejecting any `CircomData` with duplicate token addresses. Alternatively, refactor the balance-reconciliation loop in `Hinkal.transact` to aggregate `amountChanges`/`utxoAmount`/`msg.value` per unique token before comparing against the real balance delta, rather than per raw array index, so `msg.value` can only ever satisfy one aggregate equation for `address(0)`.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, and `EmporiumUpgradeable`; register Emporium as an external action.
2. Build `CircomData` with `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [V, V]`, `onChainCreation = [false, false]`, `slippageValues` satisfied, and an `EmporiumStack` whose `ops` are a no-op (or self-call that leaves Emporium's ETH balance unchanged), so `utxoAmount == 0` for both slots.
3. Generate a locally-produced proof (using the project's proving toolchain) that satisfies `inTotal[i] + amountChanges[i] === outTotal[i]` independently at slot 0 and slot 1, each claiming `V` of newly minted shielded output.
4. Call `Hinkal.transact{value: V}(...)`.
5. Assert both `require` statements in the per-token loop pass (transaction does not revert).
6. Assert: sum of minted shielded UTXO/commitment value across the two slots == `2V`, while `address(this).balance` only increased by `V` — i.e. `mintedShieldedValue > balanceDelta`, proving the equality `msg.value backing == exactly one accounting term` is violated.

Note: I could not fully verify circuit-side per-slot enforcement details (`MainEVMCircuit.circom` internals) beyond the public constraint description in scope rules; the on-chain half of the vulnerability (duplicate-address double counting in `Hinkal.sol`) is confirmed directly from the contract code cited above. [1](#0-0)

### Citations

**File:** contracts/Hinkal.sol (L76-90)
```text
            UTXO[] memory utxoSet;

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

**File:** contracts/Hinkal.sol (L97-146)
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
```

**File:** contracts/Hinkal.sol (L149-166)
```text
            if (circomData.hookData.postHookContract != address(0)) {
                ITransactHook transactHook = ITransactHook(
                    circomData.hookData.postHookContract
                );
                transactHook.afterTransact(circomData);
            }

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
