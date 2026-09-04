### Title
Slippage check provides no protection against duplicate `address(0)` entries in `erc20TokenAddresses`, enabling double-counted `balanceDif` to pass trivially - ([File: contracts/Hinkal.sol])

### Summary
`Hinkal.transact` never verifies that `circomData.erc20TokenAddresses` contains unique addresses. When the ETH placeholder `address(0)` appears twice, the per-index slippage check `require(balanceDif >= circomData.slippageValues[i])` at [1](#0-0)  is evaluated independently for each duplicate index using the *same* re-added `msg.value`, so an attacker can set `slippageValues[i]=0` for both duplicate indices and pass the check twice off a single wei of real ETH.

### Finding Description
The equality that should hold is: **one unit of real ETH sent by the attacker (`msg.value`) should be attributable to at most one slot/index in the balance-accounting loop.** Instead, for every index `i` where `circomData.erc20TokenAddresses[i] == address(0)`, the contract computes:
```solidity
balanceDif = int256(newBalances[i]) + int256(msg.value) - int256(oldBalances[i]);
``` [2](#0-1) 

`newBalances[i]` and `oldBalances[i]` come from `getBalancesForArray(circomData.erc20TokenAddresses)`, which reads the actual ETH balance of the contract for `address(0)` regardless of which index is being queried - so for two duplicate `address(0)` entries at indices 0 and 2, `newBalances[0] == newBalances[2]` and `oldBalances[0] == oldBalances[2]`. Since `msg.value` was already credited to the contract's actual balance before `transact` executes, the true delta `newBalances[i]-oldBalances[i]` already equals `msg.value` (absent other ETH movement); adding `msg.value` again yields `balanceDif = 2 * msg.value` at **both** duplicate indices independently.

There is no check anywhere in `dimensionsCheck`, `checkOnchainCreation`, or `performHinkalChecks` in `HinkalHelper.sol` ( [3](#0-2) ) that rejects duplicate entries in `circomData.erc20TokenAddresses`. Because the attacker fully controls `CircomData` (including `slippageValues`), they set `slippageValues[0] = 0` and `slippageValues[2] = 0`. The slippage require then trivially passes twice (`2*msg.value >= 0`), even though only one wei of real value entered the contract. The slippage gate's intended purpose - bounding how much of a token's real balance movement is acceptable per transact - is defeated because it operates per-index on a value (`balanceDif`) that is not actually independent across duplicate indices; it's the same inflated number reused.

This does not, by itself, move funds - it is the gate that is supposed to be the first line of defense before the downstream balance-equation `require` (lines 137-146) that determines `utxoAmount` minting. Because the slippage check passes trivially at both indices, execution proceeds to the balance-equation check for both indices, each independently allowed to justify minting UTXOs against the (falsely) doubled `balanceDif`, compounding into the insolvency described in the related UTXO-minting finding.

### Impact Explanation
This enables the protocol to mint/allow accounting for shielded value against ETH that was never actually deposited beyond the single `msg.value` — the double-counted `balanceDif` from a duplicated `address(0)` entry lets the attacker satisfy checks that should require twice the real ETH. Combined with the downstream balance-equation check, this is part of the same root cause that allows minting shielded UTXOs without full backing (Critical: minting shielded value without backing). The attacker gains the ability to create excess accounted value per transaction and this is repeatable on every call.

### Likelihood Explanation
Preconditions are minimal: attacker needs only their own valid Groth16 proof for a 3-slot `CircomData` shape with `address(0)` duplicated at two of the three token slots, and 1 wei of ETH. No privileged role, whitelisted relay, or special tree/state is required beyond a standard deposit-style transact call. Cost is 1 wei plus gas, and the exploit path is fully attacker-controlled and repeatable.

### Recommendation
Enforce uniqueness of `circomData.erc20TokenAddresses` in `dimensionsCheck` (or `performHinkalChecks`), rejecting any transaction where the same token address (including `address(0)`) appears more than once. Additionally, only add `msg.value` once globally (e.g., track whether the ETH index has already been accounted for) rather than per-iteration inside the loop over `erc20TokenAddresses`.

### Proof of Concept
Foundry test outline:
1. Deploy Hinkal with a mock verifier that accepts an attacker-crafted proof for `dimensions.tokenNumber = 3`.
2. Craft `circomData.erc20TokenAddresses = [address(0), tokenX, address(0)]`, `slippageValues = [0, sv1, 0]`, `amountChanges`/`onChainCreation` set so the balance-equation check also passes at both duplicate indices.
3. Call `transact` with `msg.value = 1 wei`.
4. Assert: at index 0, `balanceDif == 2` and `slippageValues[0] == 0` passes; at index 2, `balanceDif == 2` (same value) and `slippageValues[2] == 0` passes.
5. Assert the downstream balance-equation check at both indices is satisfied against a combined `utxoAmount`/`amountChanges` that exceeds the true 1-wei deposit, confirming double-counting propagates past the slippage gate into UTXO minting.

### Citations

**File:** contracts/Hinkal.sol (L100-104)
```text
                if (circomData.erc20TokenAddresses[i] == address(0)) {
                    balanceDif =
                        int256(newBalances[i]) +
                        int256(msg.value) -
                        int256(oldBalances[i]);
```

**File:** contracts/Hinkal.sol (L110-114)
```text
                // balance inequality to check that minimum amount of token is received/given
                require(
                    balanceDif >= circomData.slippageValues[i],
                    "slippage param is violated"
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
