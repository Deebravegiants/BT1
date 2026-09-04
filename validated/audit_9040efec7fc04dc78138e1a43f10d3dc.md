### Title
Duplicate `address(0)` entries in `erc20TokenAddresses` let `msg.value` back two independent balance equations in `Hinkal.transact` - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact()` validates the ETH balance change once per index of `circomData.erc20TokenAddresses`, but for the ETH branch (`address(0)`) it re-uses the same global `oldBalances[i]`/`newBalances[i]`/`msg.value` snapshot for every index that equals `address(0)`. Nothing in `dimensionsCheck`, `checkOnchainCreation`, or `performHinkalChecks` rejects duplicate token entries, so an attacker can list `address(0)` twice and have a single deposit of `msg.value` independently "prove" two separate per-index balance equations, each of which can back an independent shielded output commitment.

### Finding Description
The claimed equality is:

`Σ over all i of (ETH actually received by the contract) == Σ over all i where erc20TokenAddresses[i]==address(0) of (amountChanges[i] + utxoAmount[i])`

but the code checks per-index equality with a **shared, non-aggregated** left-hand side: [1](#0-0) 

For each `i`, `balanceDif` for the ETH branch is computed from `oldBalances[i]`/`newBalances[i]`, which are just `address(this).balance` snapshots taken once before/after the whole transact body (independent of `i`): [2](#0-1) [3](#0-2) 

If `circomData.erc20TokenAddresses` contains `address(0)` at two indices `i1` and `i2`, `oldBalances[i1]==oldBalances[i2]` and `newBalances[i1]==newBalances[i2]`, so `balanceDif` is identical for both entries and equals `(finalETHBalance - initialETHBalance) + msg.value`. No check anywhere (`dimensionsCheck`, `checkOnchainCreation`) rejects duplicate token addresses: [4](#0-3) 

For an internal transaction (`externalActionId == 0`), `utxoSet` stays empty, so `utxoAmount` is 0 for every index, and the per-index requirement collapses to `balanceDif == amountChanges[i]`: [5](#0-4) [6](#0-5) 

The attacker crafts `circomData` with `erc20TokenAddresses = [address(0), address(0), ...]`, `amountChanges[i1] = amountChanges[i2] = V`, `onChainCreation[i1]=onChainCreation[i2]=false`, sends `msg.value = V`. In `_internalTransact`, both positive `deltaAmountChange` entries call `transferERC20TokenFromOrCheckETH(address(0), externalAddress, address(this), V)`, which for ETH only asserts `msg.value == V` (true both times, since `msg.value` doesn't change within one call) and performs no actual transfer since `_to == address(this)`: [7](#0-6) [8](#0-7) 

After this, `balanceDif` for both `i1` and `i2` equals `V` (computed from the same single real ETH deposit), and both `require` checks in the loop pass independently: `V == amountChanges[i1]` and `V == amountChanges[i2]`. The circuit proof, being evaluated per token slot, will have generated two independent sets of output commitments (`outCommitments[i1]`, `outCommitments[i2]`) each treating `amountChanges = V` as a legitimately backed deposit for that slot, because the circuit has no cross-slot awareness that `erc20TokenAddresses[i1]==erc20TokenAddresses[i2]`. The result: two shielded UTXO sets worth `V` each (total `2V` shielded value) are created, backed by only `V` real ETH received.

The failure is that the Solidity-side balance equation is verified per-index against a shared global balance delta instead of once per unique token address (or with a duplicate-address check), while `msg.value`/balance-delta accounting is not deducted/consumed as it's matched to each index.

### Impact Explanation
An attacker can mint shielded ETH UTXOs worth `2V` while only depositing `V` real ETH into the contract (repeatable per transaction, and scales with however many duplicate `address(0)` entries `dimensions.tokenNumber` permits). This is unbacked minting of shielded value, directly causing protocol insolvency - the contract's real ETH backing becomes less than the sum of value represented by its shielded UTXO set. This matches the Critical severity category: "minting shielded value without backing."

### Likelihood Explanation
The attacker needs no privileges: any EOA can call `Hinkal.transact()` with a self-generated proof for a circuit instance where `erc20TokenAddresses` duplicates `address(0)`, `amountChanges` set as above, and `onChainCreation=false` for the internal-transaction path. The only precondition is that the circuit itself (not just `dimensionsCheck`) does not independently forbid duplicate token addresses across slots or otherwise tie per-slot ETH accounting to a single aggregate balance - this could not be fully confirmed from the Solidity code alone and would need verification against `circuits/MainEVMCircuit.circom`'s constraints, which were out of full inspection depth here. If the circuit permits generating a valid proof for such `circomData` (nothing in the reviewed Solidity checks forbids it), the attack is straightforward, costs only gas plus the deposited `V`, and is repeatable.

### Recommendation
Aggregate the ETH accounting across all indices instead of checking it independently per index: compute a single real ETH delta `(address(this).balance_after - address(this).balance_before)` once, and either (a) reject duplicate token addresses in `circomData.erc20TokenAddresses` in `dimensionsCheck`, or (b) sum `amountChanges[i] + utxoAmount[i]` for all `i` where `erc20TokenAddresses[i] == address(0)` and compare that sum once against the single aggregated ETH delta plus `msg.value`, rather than re-checking the same delta against each duplicate index independently.

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal` with a mock verifier that always returns `true` for `verifyProof` (or generate a real proof for a circuit instance matching the crafted `circomData`, per repo's circuit-testing tooling).
2. Construct `circomData` with `erc20TokenAddresses = [address(0), address(0)]`, `amountChanges = [V, V]`, `onChainCreation = [false, false]`, `externalActionData.externalActionId = 0`, `externalActionData.externalAddress = attacker`, valid `outCommitments`/`encryptedOutputs` dimensioned per `dimensions.tokenNumber = 2`.
3. Call `hinkal.transact{value: V}(a, b, c, dimensions, circomData)`.
4. Assert both `require` checks in the balance-equation loop pass (transaction succeeds).
5. Assert `address(hinkal).balance - balanceBefore == V` (only `V` real ETH received) while two `insertCommitments` calls have registered on-chain/off-chain UTXOs whose sum of declared shielded value equals `2V`.
6. Equality to test explicitly: `address(hinkal).balance_after - address(hinkal).balance_before` (== V) vs. sum of `amountChanges[i]` for the two duplicate `address(0)` slots (== 2V) - demonstrate these differ, proving unbacked minting.

Note: full confirmation requires checking that `circuits/MainEVMCircuit.circom` does not itself forbid duplicate `erc20TokenAddresses` entries across token slots; this circuit-side constraint could not be fully verified within the scope of this review and should be checked before treating this as conclusively exploitable.

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

**File:** contracts/Hinkal.sol (L172-230)
```text
    function _internalTransact(CircomData calldata circomData) private {
        bool hasPaidToRelay = false;
        for (uint64 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 deltaAmountChange = _calculateDeltaAmount(circomData, i);

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
            } else {
                uint256 sumAbs = uint256(-deltaAmountChange);
                uint256 relayFee = 0;
                if (circomData.relay != address(0)) {
                    uint256 flatFee = circomData.feeStructure.feeToken ==
                        circomData.erc20TokenAddresses[i]
                        ? circomData.feeStructure.flatFee
                        : 0;

                    require(
                        sumAbs >= flatFee,
                        "Relay Fee is over withdraw amount"
                    );

                    uint256 recipientAmount = ((10000 -
                        circomData.feeStructure.variableRate) *
                        (sumAbs - flatFee)) / 10000;

                    relayFee = sumAbs - recipientAmount;

                    if (relayFee > 0) {
                        transferERC20TokenOrETH(
                            circomData.erc20TokenAddresses[i],
                            circomData.relay,
                            relayFee
                        );
                    }
                    hasPaidToRelay = true;
                }
                if (sumAbs - relayFee > 0) {
                    transferERC20TokenOrETH(
                        circomData.erc20TokenAddresses[i],
                        circomData.externalActionData.externalAddress,
                        sumAbs - relayFee
                    );
                }
            }
        }
        require(
            circomData.relay == address(0) || hasPaidToRelay,
            "relay not paid"
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

**File:** contracts/Transferer.sol (L111-128)
```text
    function transferERC20TokenFromOrCheckETH(
        address _contractAddress,
        address _from,
        address _to,
        uint256 _value
    ) internal {
        if (_contractAddress == address(0)) {
            require(
                msg.value == _value,
                "msg.value doesn't match needed amount"
            );
            if (_to != address(this)) {
                transferETH(_to, _value);
            }
        } else {
            transferERC20TokenFrom(_contractAddress, _from, _to, _value);
        }
    }
```
