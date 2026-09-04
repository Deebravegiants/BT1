### Title
Unspent input tokens after LI.FI swap are never refunded, permanently trapping user shielded funds - (File: contracts/external-actions/swaps/ExternalActionSwap.sol)

### Summary
`ExternalActionSwap.swap()` (used by `LifiExternalAction`) transfers the *entire* proven input amount out of the Hinkal shielded pool to itself before the swap, but only ever forwards the *output* token balance delta back to the user. If the external router call does not consume the full approved `inputAmount` (e.g., partial fill, aggregator route consuming less than the max-approved allowance, or any deviation between the proof-declared amount and what `externalActionMetadata` actually pulls), the leftover input tokens remain stuck in the `ExternalActionSwap`/`LifiExternalAction` contract with no refund path and no rescue/sweep function anywhere in the codebase.

### Finding Description
In `_externalTransact` (`contracts/Hinkal.sol`), the full declared `deltaAmountChanges[i]` (the negative delta, i.e. the committed input amount proven by the circuit) is transferred from Hinkal to the external action address *before* `runAction` is invoked: [1](#0-0) 

`ExternalActionSwap.swap()` then computes `inputAmount` from this same delta and calls `callRouter`, which unconditionally grants `type(uint256).max` allowance to the router and executes the arbitrary `externalActionMetadata` calldata: [2](#0-1) 

The amount actually returned to the caller is derived solely from the *output* token balance delta (`swappedAmount = getERC20OrETHBalance(outputToken) - balanceBefore`), never checked against `inputAmount` actually consumed: [3](#0-2) 

There is no logic anywhere in `swap()` that checks the input-token balance before/after the router call and refunds any unconsumed remainder. `TransfererBase.approveUnlimited` grants max allowance rather than an allowance capped to `inputAmount`, so the router is free to pull less than the full amount without reverting: [4](#0-3) 

Back in `Hinkal.transact`, the top-level balance equation only verifies that the amount that left Hinkal's own balance matches `circomData.amountChanges[i]` plus the newly created UTXOs — it has no visibility into what the external action contract actually did with the funds internally: [5](#0-4) 

This is the same root-cause class as the referenced Superposition `swap_2_internal` finding: an amount charged to the user (`original_amount`/`inputAmount`) that is not fully consumed by the underlying swap is never returned, so `amount actually used by swap + amount refunded` breaks equality with `amount taken from the user`. Here, because there is no owner/admin rescue function on `ExternalActionSwap`/`ExternalActionBaseV2`/`OwnerHinkal` (no `withdraw`/`rescue`/`sweep` function found), any residual input tokens are **permanently** stuck in the external action contract, unlike the C4 case where at least an owner could plausibly intervene.

### Impact Explanation
This is a permanent freezing of user funds: the shielded balance debited from the user (via the nullifier/commitment accounting in `Hinkal.transact`) is strictly `inputAmount`, but only part of that value may be realized as output UTXO value if the router under-consumes the input. The difference is unrecoverable dust/value trapped in the external action contract forever, since no sweep mechanism exists. This falls under the specified High impact category "temporary/permanent freezing of user funds" (here, permanent, given no rescue function exists).

### Likelihood Explanation
Likelihood depends on how deterministic/atomic the LI.FI router calldata's consumption of `inputAmount` is. Since `approveUnlimited` grants unrestricted allowance rather than exactly `inputAmount`, any underlying integration/path chosen by LI.FI that does not consume the entire approved/expected amount (e.g. certain bridge/aggregator routes, fee-on-transfer tokens, or routes with independent slippage handling that leave dust) would trigger this without any additional attacker action — it can occur in normal operation, not just via active exploitation, making it a real (if externally-router-dependent) risk rather than purely theoretical.

### Recommendation
In `ExternalActionSwap.swap()` / `LifiExternalAction.callRouter`, measure the input token balance before and after the router call (mirroring what's already done for `outputToken`), and if `inputAmount` is not fully consumed, refund the unspent input token back to `msg.sender` (Hinkal) so it can be re-included in the created UTXO / balance equation, analogous to the recommended fix in the referenced report:
```solidity
uint256 inputBalanceBefore = getERC20OrETHBalance(inputToken);
...
uint256 inputBalanceAfter = getERC20OrETHBalance(inputToken);
uint256 unspent = inputBalanceBefore - inputBalanceAfter < inputAmount
    ? inputAmount - (inputBalanceBefore - inputBalanceAfter)
    : 0;
if (unspent > 0) {
    transferERC20TokenOrETH(inputToken, msg.sender, unspent);
}
```
Also consider capping approvals to `inputAmount` instead of `type(uint256).max` to limit exposure to router behavior.

### Proof of Concept
1. User submits a `transact` call with `externalActionId` pointing to `LifiExternalAction`, declaring `amountChanges[0] = -inputAmount` for `token1`.
2. `Hinkal._externalTransact` transfers `inputAmount` of `token1` to `LifiExternalAction`.
3. `LifiExternalAction.callRouter` approves the LI.FI router for `type(uint256).max` and executes `externalActionMetadata`, a route that (due to aggregator routing, dust handling, or partial-fill behavior) only consumes `amount_in < inputAmount` of `token1`, delivering `swappedAmount` of `outputToken`.
4. `swap()` computes `amountToSendToHinkal` purely from `outputToken`'s balance delta and forwards only that to Hinkal; the leftover `inputAmount - amount_in` of `token1` remains in `LifiExternalAction`'s balance.
5. Hinkal's balance-equation check in `transact` passes (its own `token1` balance decreased by exactly `inputAmount`, matching `amountChanges[0]`), so the transaction completes normally, and the leftover `token1` is permanently stranded in `LifiExternalAction` with no function available to retrieve it.

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

**File:** contracts/Hinkal.sol (L247-256)
```text
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

**File:** contracts/external-actions/swaps/LifiExternalAction.sol (L16-36)
```text
    function callRouter(
        address inputToken,
        uint256 inputAmount,
        address outputToken,
        bytes calldata externalActionMetadata
    ) internal override returns (uint256 swappedAmount) {
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

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L63-93)
```text
        uint256 swappedAmount = callRouter(
            inputToken,
            inputAmount,
            outputToken,
            circomData.externalActionData.externalActionMetadata
        );

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

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
```

**File:** contracts/TransfererBase.sol (L32-43)
```text
    function approveUnlimited(
        address _erc20TokenAddress,
        address _to
    ) internal {
        if (
            IERC20(_erc20TokenAddress).allowance(address(this), _to) <
            type(uint256).max / 2
        ) {
            IERC20(_erc20TokenAddress).safeApprove(_to, 0);
            IERC20(_erc20TokenAddress).safeApprove(_to, type(uint256).max);
        }
    }
```
