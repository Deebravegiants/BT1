### Title
Swap flat fee to an arbitrary `feeToken` bypasses the Hinkal balance equation, allowing silent drain of protocol-held tokens - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap.swap()` pays the relay's flat fee in `circomData.feeStructure.feeToken`, a value fully controlled by the transaction's prover/relay and independent of the two tokens (`erc20TokenAddresses[0]`/`[1]`) that the enclosing `Hinkal.transact()` balance equation actually verifies. When `feeToken` differs from both the input and output token of the swap, the flat fee is transferred out of the Hinkal contract in a token that is never included in the pre/post balance snapshot, so the core "change in balance == change in off-chain + on-chain UTXOs" invariant never sees this outflow.

### Finding Description
`Hinkal.transact()` computes `oldBalances`/`newBalances` and enforces the balance equation only for `circomData.erc20TokenAddresses`: [1](#0-0) [2](#0-1) 

`ExternalActionSwap.swap()` operates on exactly two tokens, `erc20TokenAddresses[0]` (input) and `[1]` (output): [3](#0-2) 

But the relay's flat fee is always denominated in `circomData.feeStructure.feeToken`, which is an arbitrary, prover-chosen address unconstrained to be one of these two tokens: [4](#0-3) 

If `feeToken` is neither `inputToken` nor `outputToken`, the code enters the `else` branch and calls `sendToRelay(circomData.relay, relayFee, circomData.feeStructure.feeToken)`, moving `flatFee` of that third, uninvolved token out of the Hinkal contract. Because `erc20TokenAddresses` only contains the two swap tokens, `getBalancesForArray` in `Hinkal.transact()` never samples the `feeToken` balance before/after the call, so this transfer is completely invisible to the balance-diff check in `Hinkal.sol:134-147`. The `FeeStructure` itself is only integrity-checked via `calldataHash`/`signedMessageHash` (i.e., it's part of the signed data, not re-derived or bounded to the tx's tokens) in `CircomDataBuilder`/`HinkalHelper`: [5](#0-4) [6](#0-5) 

There is no check anywhere (in `dimensionsCheck`, `checkOnchainCreation`, or the swap logic) constraining `feeStructure.feeToken` to be a member of `erc20TokenAddresses`. This breaks the intended equality: "change in Hinkal's on-chain ERC20 balance must equal the sum of committed off-chain UTXO changes and newly created on-chain UTXOs," because a value-bearing outflow (`feeToken` balance decreasing by `flatFee`) occurs with zero corresponding entry in `amountChanges`/`utxoAmount`/nullifiers for that token.

### Impact Explanation
This lets whoever controls the signed `CircomData` for a swap transaction (the transaction's own signer for a self-relayed swap, or a relay for a relayed one, both of which set `feeStructure`) siphon a `flatFee` amount of any arbitrary ERC-20 token that happens to be held by the Hinkal contract (i.e., other users' shielded protocol funds) to `circomData.relay`, without ever debiting any user's UTXO for that token and without the invariant check catching it. This is theft of protocol/user-pooled funds in a token unrelated to the transaction, satisfying "High – theft ... of protocol/relay fees" or potentially "Critical – direct theft of shielded ... user funds" depending on whether the drained token is part of the shielded pool balance.

### Likelihood Explanation
The path requires only an unprivileged prover/relay to set `feeStructure.feeToken` to a third-party token address while running a normal `ExternalActionSwap`-derived swap (e.g., `swap(circomData, deltaAmounts)`); this is entirely within the domain the prover already signs and controls, no admin/relay allowlisting bypass or oracle assumption is needed, and no additional preconditions exist beyond the target token being held with nonzero balance by the Hinkal contract (a normal steady-state condition given other users' shielded deposits sit there).

### Recommendation
Constrain `feeStructure.feeToken` to be one of `circomData.erc20TokenAddresses` (ideally the swap's `inputToken` or `outputToken`) via an explicit `require` in `dimensionsCheck`/`checkOnchainCreation` (or directly in `ExternalActionSwap.swap()`), and/or fold the `feeToken` into `erc20TokenAddresses` so that `getBalancesForArray` samples it and the balance equation in `Hinkal.sol` captures the outflow.

### Proof of Concept
1. Attacker (self-relaying, so `circomData.relay == circomData.externalActionData... ` acting as their own relay, or a colluding relay) crafts a swap transaction with `erc20TokenAddresses = [TokenA, TokenB]` (a legitimate swap pair) but sets `feeStructure.feeToken = TokenC`, where `TokenC` is a token with nonzero balance held by the Hinkal contract (from other users' shielded UTXOs) and `feeStructure.flatFee = X`.
2. Since `feeToken (TokenC)` is neither `TokenA` nor `TokenB`, `TokenC` never appears in `circomData.erc20TokenAddresses`, so `Hinkal.transact()`'s `getBalancesForArray`/balance-diff check (`contracts/Hinkal.sol:76-147`) never inspects `TokenC`.
3. `ExternalActionSwap.swap()` executes the `TokenA -> TokenB` swap normally, then hits the `else` branch at `contracts/external-actions/swaps/ExternalActionSwap.sol:80-86`, calling `sendToRelay(circomData.relay, X, TokenC)`, moving `X` of `TokenC` from the Hinkal contract to `circomData.relay`.
4. `Hinkal.transact()`'s balance/UTXO equation for `TokenA` and `TokenB` still balances correctly (since neither is affected), so the transaction succeeds, and the proof/circuit (which never references `feeStructure.feeToken` as a public/private signal governing balances) has no way to reject it.
5. Net effect: `X` units of `TokenC`, backing other users' shielded balances, are transferred out to `circomData.relay` with no nullifier spent and no balance-equation violation — an unbacked reduction of the shielded pool for `TokenC`.

Note: I was unable to fully trace how `feeStructure.feeToken`/`relay` values interact with off-chain relayer/prover trust assumptions or whether any off-chain infrastructure (not in this repo) additionally restricts `feeToken` choices; this analysis is based solely on on-chain contract logic in the indexed files.

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

**File:** contracts/Hinkal.sol (L134-147)
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
            }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L44-51)
```text
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];
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

**File:** contracts/HinkalHelper.sol (L221-225)
```text
        require(
            CircomDataBuilder.getHashedCalldata(circomData) ==
                circomData.calldataHash,
            "Calldata Hash Integrity Check Failed"
        );
```

**File:** contracts/types/CircomData.sol (L6-10)
```text
struct FeeStructure {
    address feeToken;
    uint256 flatFee;
    uint256 variableRate; // measured in beeps = 0.01 of 1%
}
```
