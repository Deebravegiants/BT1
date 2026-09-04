### Title
Arbitrary `feeStructure.feeToken` lets a swap siphon an untracked token's pooled balance to the relay - (File: `contracts/external-actions/swaps/ExternalActionSwap.sol`)

### Summary
`ExternalActionSwap.swap` pays the flat relay fee in `circomData.feeStructure.feeToken` whenever that token differs from the swap's `outputToken`, without ever requiring `feeToken` to be one of the two tokens declared in `circomData.erc20TokenAddresses` (`inputToken`/`outputToken`). Because `Hinkal.sol`'s balance-equality check only iterates over `circomData.erc20TokenAddresses` [1](#0-0) , a transfer of an arbitrary third token out of the shared pool is never reconciled against any `amountChanges`/UTXO accounting, letting a normal user drain that token's shielded reserve to a relay.

### Finding Description
In `swap()`, `relayFee` is always set to `circomData.feeStructure.flatFee` and is sent in `circomData.feeStructure.feeToken`: [2](#0-1) 

Nothing in this function, in `ExternalActionBaseV2`, in `HinkalHelper.performHinkalChecks`/`dimensionsCheck` [3](#0-2) , or in the circuit-side public-input construction in `CircomDataBuilder.sol` [4](#0-3)  constrains `feeStructure.feeToken` to be equal to `inputToken` or `outputToken`. A search of the `circuits/**` tree found no constraint tying `feeStructure` to `erc20TokenAddresses` either.

`feeStructure` is only used to build `calldataHash`/the signed-message hash, so it is fully attacker-controlled data that the prover/signer (the attacker themselves, as an ordinary user) is free to set to any value and still produce a valid proof and signature for their own transaction — no relayer or admin key is required to construct it.

`Hinkal.transact()`'s balance-equality check is the sole invariant guaranteeing that on-chain token movement matches the claimed `amountChanges`/UTXO deltas, but it only loops over `circomData.erc20TokenAddresses` [1](#0-0) . If a user submits a swap with `erc20TokenAddresses = [inputToken, outputToken]` and sets `feeStructure.feeToken = X` where `X` is neither `inputToken` nor `outputToken`, the `sendToRelay(circomData.relay, relayFee, X)` call moves `flatFee` worth of `X` out of the contract's pooled balance, and this movement is invisible to the equality check because `X` is not part of the iterated array — it breaks the equality "on-chain balance change of a token == its `amountChanges` + its UTXO delta" for token `X`, which never even gets evaluated.

### Impact Explanation
This siphons value from the protocol's shared pool of an arbitrary ERC20 (which backs other users' shielded UTXOs of that token) to the relay, with no corresponding debit recorded anywhere in the Merkle-tree/UTXO accounting. That is a direct theft of shielded user funds of the untracked token, executable repeatedly by any user who can get a swap transaction relayed, rated Critical per the theft-of-shielded-funds category.

### Likelihood Explanation
Any unprivileged EOA can craft `circomData` for a normal swap and simply set `feeStructure.feeToken` to a token address unrelated to the swap pair; this requires no special privilege, only a valid proof of a legitimate small swap and a willing/oblivious relay to submit it (relays are expected to relay well-formed transactions and are not shown to validate `feeToken` against the swap pair). The check that stops this would need to enforce `feeToken == inputToken || feeToken == outputToken` (or include `feeToken` in the tracked-token balance equation), which is currently absent.

### Recommendation
In `ExternalActionSwap.swap`, require `circomData.feeStructure.feeToken == inputToken || circomData.feeStructure.feeToken == outputToken` before paying `relayFee`, or otherwise include `feeStructure.feeToken` in the set of tokens whose balance changes are reconciled by `Hinkal.transact()`'s balance-equality loop so any movement of an untracked token is rejected.

### Proof of Concept
1. User prepares a normal swap transaction (`erc20TokenAddresses = [TokenA, TokenB]`) through `ExternalActionSwap`/`Hinkal.transact`.
2. User sets `circomData.feeStructure = { feeToken: TokenC, flatFee: F, variableRate: r }`, where `TokenC` is any ERC20 the Hinkal pool holds a balance of (backing other users' shielded notes) and is not `TokenA`/`TokenB`.
3. Since `feeStructure` only feeds into `calldataHash`/`signedMessageHash` (self-signed by the user) and is never checked against `erc20TokenAddresses`, the proof/signature verify normally.
4. During execution, `swap()` hits the `else` branch (`feeToken != outputToken`) and calls `sendToRelay(circomData.relay, F, TokenC)`, moving `F` units of `TokenC` from the contract to the relay [5](#0-4) .
5. `Hinkal.transact()`'s balance-equality loop only checks `TokenA`/`TokenB` [1](#0-0) , so the `TokenC` deficit is never detected, silently reducing the pool backing other users' `TokenC` shielded balances.

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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-87)
```text
        uint256 relayFee = circomData.feeStructure.flatFee;

        uint256 hinkalFee = hinkalHelper.calculateRelayFee(
            swappedAmount,
            0,
            circomData.feeStructure.variableRate
        );

        if (circomData.feeStructure.feeToken == outputToken) {
            sendToRelay(circomData.relay, relayFee + hinkalFee, outputToken);
        } else {
            sendToRelay(
                circomData.relay,
                relayFee,
                circomData.feeStructure.feeToken
            );
            sendToRelay(circomData.relay, hinkalFee, outputToken);
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

**File:** contracts/CircomDataBuilder.sol (L37-54)
```text
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
