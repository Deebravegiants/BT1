### Title
Unspent ETH forwarded to the LI.FI router in `LifiExternalAction` is permanently stranded with no refund path - (File: `contracts/external-actions/swaps/LifiExternalAction.sol`)

### Summary
`LifiExternalAction.callRouter()` forwards the entire computed `inputAmount` as `msg.value` to the external LI.FI `router` when swapping from native ETH, exactly mirroring the analog bug class from the external report (SwapRouter not refunding unspent ETH). If the router's call consumes less than the full amount sent (partial fill, positive slippage, price-limit/liquidity truncation in the underlying DEX route), the leftover ETH remains in the `LifiExternalAction` contract's balance, and there is no function anywhere in this contract, `ExternalActionSwap`, `ExternalActionBaseV2`, or `Transferer` to reclaim or refund it.

### Finding Description
In `LifiExternalAction.callRouter()`: [1](#0-0) 

the contract computes `swappedAmount` purely from the change in `outputToken` balance, never checking whether all of the forwarded ETH (`inputAmount`) was actually consumed by `router.call{value: inputAmount}(...)`. The `inputAmount` itself is derived in `ExternalActionSwap.swap()` from the (already fee-adjusted) `deltaAmounts[0]` computed off-chain by the prover: [2](#0-1) 

Hinkal's core balance equation in `Hinkal.sol` assumes that once the full `inputAmount` is transferred from Hinkal to `circomData.externalActionData.externalAddress` (the `LifiExternalAction` contract), that value is fully accounted for by the external action's output UTXO plus fees: [3](#0-2) 

But nothing enforces that the LI.FI router actually spends 100% of the ETH it was given. Any leftover ETH (e.g., because the LI.FI-aggregated route achieves a better price, hits a liquidity/price-limit constraint mid-route, or otherwise underspends) is retained as a balance in `LifiExternalAction`, outside of the `calldataHash`/proof-verified equality that Hinkal enforces. Unlike the reported Uniswap `SwapRouter`, which at least exposes a permissionless `refundETH()` to reclaim leftover ETH (albeit stealable by anyone), `LifiExternalAction` has **no refund/sweep mechanism at all** — I confirmed via search that no `withdraw`/`rescue`/`sweep` function exists in `Hinkal.sol`, `RelayStore.sol`, `IWrapper.sol`, `ExternalActionBaseV2.sol`, or `Transferer.sol` that could recover ETH accidentally stuck in an external action contract. The only functions on `ExternalActionBaseV2` are `setAllowedRecipients` and `runAction`: [4](#0-3) 

This means user ETH that is not fully consumed by the LI.FI router's swap is permanently locked in the `LifiExternalAction` contract — it breaks the value-conservation equality Hinkal expects (input value in = output value out + fees) because value that left the shielded system via the `externalActionData.externalAddress` transfer is never fully returned to the user's new UTXO nor accessible to anyone.

### Impact Explanation
This is a permanent freezing of user funds: any ETH not consumed in the LI.FI swap call is irrecoverably locked in the `LifiExternalAction` contract with no code path (owner or otherwise) to withdraw it. Per the severity classification given, "permanent freezing of user funds" is Critical impact.

### Likelihood Explanation
Likelihood is high because LI.FI is an aggregator/router of routers; any underlying DEX leg it routes through can behave like the analog Uniswap `SwapRouter` (partial fill due to price limits, insufficient liquidity, or favorable slippage), and this requires no privileged access — it happens on ordinary ETH-input swaps executed through the normal `Hinkal.transact` → `_externalTransact` → `LifiExternalAction.runAction` → `swap` → `callRouter` flow.

### Recommendation
In `LifiExternalAction.callRouter()`, after the `router.call{value: inputAmount}(...)` for the native-ETH branch, capture the ETH balance before/after the call (similar to how `outputToken` balance is measured) and refund any unspent ETH back to the calling context (ultimately crediting the user, e.g. by including it into `swappedAmount`'s accounting or by explicitly returning leftover ETH so it can be folded back into the resulting UTXO / relayed back to the Hinkal caller) rather than letting it remain trapped in the external action contract.

### Proof of Concept
1. A user deposits shielded ETH and initiates an ETH→ERC20 swap via `Hinkal.transact`, routed to `LifiExternalAction` with `inputToken == address(0)` and `inputAmount = X`.
2. `Hinkal._externalTransact` transfers `X` ETH to `LifiExternalAction` per `deltaAmountChanges[0]`: [5](#0-4) 
3. `LifiExternalAction.callRouter` forwards all `X` ETH to `router.call{value: X}(externalActionMetadata)`: [6](#0-5) 
4. Suppose the underlying LI.FI route only needs `X - Δ` ETH to complete the swap (e.g., a DEX leg hits a price/liquidity boundary or achieves favorable execution), leaving `Δ` ETH in the router or bounced back to `LifiExternalAction`'s balance (depending on router semantics) after the external call returns.
5. `swappedAmount` is computed solely from `outputToken` balance delta, so the leftover `Δ` ETH is never detected, refunded, or included in the resulting UTXO amount sent to `msg.sender`: [7](#0-6) 
6. `Δ` ETH remains stuck in `LifiExternalAction`'s balance indefinitely, since no function in the codebase can withdraw or sweep it out — permanently freezing that portion of the user's shielded funds.

Note: I was not able to fully verify the exact byte-level behavior of the LI.FI router's `.call` (e.g., whether it always internally forwards 100% of provided `msg.value` deeper into its own aggregated route with its own guarantees) since the LI.FI router itself is out of scope/external, so the precise probability of leftover-ETH scenarios depends on the specific route LI.FI selects at call time — this mirrors the exact same external-dependency caveat noted in the original report about Uniswap's `SwapRouter`.

### Citations

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L22-36)
```text
        uint256 balanceBefore = getERC20OrETHBalance(outputToken);

        if (inputToken == address(0)) {
            (bool success, ) = router.call{value: inputAmount}(
                externalActionMetadata
            );
            require(success, "LI.FI swap failed: native coin");
        } else {
            approveUnlimited(inputToken, router);
            (bool success, ) = router.call(externalActionMetadata);
            require(success, "LI.FI swap failed: erc-20 token");
        }

        swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore;
    }
```

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L40-68)
```text
    function swap(
        CircomData calldata circomData,
        int256[] calldata deltaAmounts
    ) internal returns (UTXO[] memory utxoSet) {
        address inputToken = circomData.erc20TokenAddresses[0];
        uint256 inputAmount = uint256(-deltaAmounts[0]);

        if (inputToken == circomData.feeStructure.feeToken) {
            inputAmount -= circomData.feeStructure.flatFee;
        }

        address outputToken = circomData.erc20TokenAddresses[1];

        require(
            circomData.slippageValues[1] != 0,
            "swap output slippage floor not set"
        );

        require(
            block.timestamp <= circomData.timeStamp + SWAP_DEADLINE_WINDOW,
            "swap expired"
        );

        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );
```

**File:** contracts/Hinkal.sol (L100-146)
```text
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

**File:** contracts/Hinkal.sol (L244-256)
```text
        int256[] memory deltaAmountChanges = new int256[](
            circomData.erc20TokenAddresses.length
        );
        for (uint256 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            deltaAmountChanges[i] = _calculateDeltaAmount(circomData, i);
            if (deltaAmountChanges[i] < 0) {
                transferERC20TokenOrETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    uint256(-deltaAmountChanges[i])
                );
            }
        }
```

**File:** contracts/external-actions/ExternalActionBaseV2.sol (L30-42)
```text
    function setAllowedRecipients(
        address[] calldata recipients
    ) external onlyOwner {
        for (uint i = 0; i < recipients.length; i++) {
            require(recipients[i] != address(0), "zero address!");
            isAllowedRecipient[recipients[i]] = true;
        }
    }

    function runAction(
        CircomData calldata circomData,
        int256[] calldata deltaAmountChanges
    ) external virtual returns (UTXO[] memory utxoSet) {}
```
