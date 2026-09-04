### Title
Duplicate `address(0)` entries in `erc20TokenAddresses` allow `msg.value` to be counted once per occurrence, minting shielded ETH value without backing - (File: contracts/Hinkal.sol)

### Summary
`Hinkal.transact` computes `balanceDif` for each index `i` of `circomData.erc20TokenAddresses` independently, and for the native asset it adds the *entire* `msg.value` to every index whose address equals `address(0)`, since `msg.value` is a fixed transaction-level value that Solidity never decrements. No check in `dimensionsCheck`, `checkOnchainCreation`, or elsewhere enforces that `erc20TokenAddresses` entries are unique. This lets an attacker list `address(0)` twice (or more), pass the per-index `balanceDif == amountChanges[i] + utxoAmount` equality at every occurrence using the same single ETH deposit, and mint multiple independent shielded/on-chain UTXO credits worth the deposited amount from only one real transfer of ETH.

### Finding Description
The equality the protocol relies on is: **net ETH entering Hinkal in the call == sum of `amountChanges` credited + sum of on-chain UTXO amounts minted**, checked per-token index in [1](#0-0) .

For `erc20TokenAddresses[i] == address(0)`, `balanceDif` is computed as:
```
balanceDif = int256(newBalances[i]) + int256(msg.value) - int256(oldBalances[i]);
``` [2](#0-1) 

`msg.value` is a constant for the whole transaction; it is not reduced as it is "spent" internally. `transferERC20TokenFromOrCheckETH` for `address(0)` only asserts `msg.value == _value` and, when `_to == address(this)`, performs no actual transfer at all: [3](#0-2) . Consequently this check can be satisfied repeatedly for multiple indices using the *same* `msg.value`, since it never verifies that the ETH has not already been "claimed" by an earlier index.

There is no uniqueness requirement on `circomData.erc20TokenAddresses` anywhere in `dimensionsCheck` or `checkOnchainCreation` [4](#0-3) ; only lengths are checked to match `dimensions.tokenNumber`. The ZK circuit's `inTotal + amountChanges === outTotal` constraint (per `MainEVMCircuit.circom`) is evaluated per index/slot of the public input array and, as far as could be verified from what is indexed, does not cross-check that two slots referring to the same on-chain token address are economically consistent with a single native-asset deposit.

**Attacker's call:** invoke `Hinkal.transact` with `erc20TokenAddresses = [address(0), <other tokens>..., address(0)]` (duplicate native-asset slot at two different indices, e.g., index 0 and index k), sending `msg.value = X`. For index 0: set `amountChanges[0] = X`, `onChainCreation[0] = false`, and have the proof mint an off-chain (or on-chain) UTXO note of `X` native ETH. For index k: likewise set `amountChanges[k] = X` and mint a second independent UTXO note of `X` native ETH. Since no real ETH transfer occurs for either "deposit" leg (destination is `address(this)`, `_to == address(this)` path, no transfer), `newBalances[0] == oldBalances[0]` and `newBalances[k] == oldBalances[k]`. Then:
- `balanceDif[0] = 0 + X - 0 = X == amountChanges[0] (X) + utxoAmount[0] (0)` → holds.
- `balanceDif[k] = 0 + X - 0 = X == amountChanges[k] (X) + utxoAmount[k] (0)` → holds.

Both per-index balance checks pass even though only `X` ETH was actually received by the contract once, while the circuit-verified shielded ledger is credited `2X` in aggregate. This produces shielded value with no backing, i.e., protocol insolvency for the native asset.

### Impact Explanation
This mints shielded UTXO value that is not backed by any corresponding asset transfer into the vault, matching the Critical category "minting shielded value without backing (protocol insolvency)". Each occurrence of `address(0)` beyond the first in `erc20TokenAddresses` effectively lets the attacker double (or N-times) count a single ETH deposit. The attack is repeatable per transaction (bounded only by array-length/gas limits and dimension constraints) and can be executed by any unprivileged depositor.

### Likelihood Explanation
Preconditions are modest: the attacker must be able to construct a valid `CircomData`/proof with `erc20TokenAddresses` containing `address(0)` at two (or more) distinct indices with independently-verified `amountChanges`, which requires generating a legitimate proof for their own note tree (something explicitly listed as attacker capability). No privileged role, relayer collusion, or oracle manipulation is required. The main open question — and the reason I cannot state this with full certainty — is whether the Circom circuit (`MainEVMCircuit.circom`) enforces uniqueness of token addresses across the `tokenNumber` slots as part of its public-input binding; I was not able to fully inspect that constraint before running out of investigation budget. If the circuit does enforce distinct token addresses per slot (or ties `amountChanges[i]` to a token-address Merkle/set check that rejects duplicates), this exact path would be blocked at the proof level and the vulnerability would not be exploitable. This uncertainty must be resolved by inspecting `circuits/MainEVMCircuit.circom` in full (which was excluded from what I could confirm) before treating this as an actionable finding.

### Recommendation
- In `Hinkal.transact` (or `dimensionsCheck`), explicitly enforce that `circomData.erc20TokenAddresses` contains no duplicate addresses (including no duplicate `address(0)` entries) before performing the per-index balance checks.
- Alternatively, aggregate `balanceDif` per unique token address once (summing all `amountChanges`/`utxoAmount` mapped to that address) instead of trusting index-based verification when the same real-world balance can appear at multiple indices.
- If wrapped-native handling alongside raw `address(0)` is an intended feature, ensure `msg.value` is "consumed" exactly once across the whole loop (e.g., track a `msgValueUsed` accumulator and require `sum(msg.value contributions) == msg.value`, rather than re-adding the full `msg.value` at every native-asset index).

### Proof of Concept
Foundry test plan:
1. Deploy `Hinkal`, `HinkalHelper`, a verifier stub or use a locally-generated proof for a `CircomData` with `dimensions.tokenNumber = 2`, `erc20TokenAddresses = [address(0), address(0)]`.
2. Set `amountChanges = [X, X]`, `onChainCreation = [false, false]`, matching off-chain output UTXOs of value `X` each (or on-chain if externalActionId != 0 permits on-chain creation), with valid `inputNullifiers`/`outCommitments` satisfying the circuit's per-slot `inTotal + amountChanges === outTotal`.
3. Call `hinkal.transact{value: X}(a, b, c, dimensions, circomData)`.
4. Assert: `address(hinkal).balance - preBalance == X` (only one deposit of real ETH occurred).
5. Assert: sum of newly inserted shielded UTXO commitments' represented native-ETH value == `2X` (via decrypting/verifying the two output notes off-chain, or via `utxoAmount`/on-chain commitment count if on-chain creation used).
6. Confirm both per-index `require(balanceDif == ...)` checks in `Hinkal.transact` passed (transaction does not revert), demonstrating `vault ETH inflow (X) < credited shielded UTXO value (2X)`.

### Citations

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
