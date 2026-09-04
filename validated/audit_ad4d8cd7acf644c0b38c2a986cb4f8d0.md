### Title
Stranded relay-fee dust in `ExternalActionSwap` can be siphoned by an attacker via the persistent unlimited router approval - (File: contracts/external-actions/swaps/ExternalActionSwap.sol, contracts/external-actions/swaps/LifiExternalAction.sol)

### Summary
`ExternalActionSwap.swap` computes the fee to withhold (`totalFee`) unconditionally from `swappedAmount`, but only forwards it to the relay when `circomData.relay != address(0)` [1](#0-0) . When a user submits a transaction with `relay == address(0)` (a legitimate, self-relayed / zero-effective-fee path), `sendToRelay` becomes a no-op [2](#0-1) , so `totalFee` worth of the output token is neither sent to the relay nor to Hinkal (`amountToSendToHinkal = swappedAmount - totalFee`) - it is stranded in the `ExternalActionSwap` contract. Because `LifiExternalAction.callRouter` grants the router an unlimited, non-resetting ERC20 approval (`approveUnlimited(inputToken, router)`) [3](#0-2)  and passes fully attacker-controlled `externalActionMetadata` straight to `router.call(...)`, an attacker can, in a later transaction where the stranded token is the input token, craft LI.FI calldata that pulls both their own legitimately-transferred `inputAmount` and the pre-existing stranded balance through that lingering approval, swap it all, and have the entire resulting `swappedAmount` credited to their own output UTXO.

### Finding Description
Broken equality: *tokens leaving the action contract in a tx* should equal *-deltaAmountChanges Hinkal sent it that tx* (plus the swap's genuine output). In practice, `swappedAmount` in `LifiExternalAction.callRouter` is derived purely from the output-token balance delta bracketing the router call [4](#0-3) , with no constraint tying the *input* side actually consumed by the router back to `-deltaAmounts[0]`. The router pulls whatever amount the attacker encodes in `externalActionMetadata`, up to the unlimited allowance already granted from prior calls.

Exploit flow:
1. Attacker (or anyone) submits a swap transaction with `circomData.relay == address(0)`. `totalFee` (relay fee and/or hinkal fee when `outputToken == feeToken`) is computed and subtracted from `swappedAmount`, but since `sendToRelay` short-circuits on `relay == address(0)`, this fee amount is never transferred out - it remains as dust in the `ExternalActionSwap`/`LifiExternalAction` contract [5](#0-4) .
2. In a subsequent transaction, the attacker sets `erc20TokenAddresses[0]` (the input token) equal to the token that is now stranded in the contract. Hinkal's `_externalTransact` sends only `-deltaAmountChanges[0]` (the attacker's own committed amount) to the action [6](#0-5) .
3. The attacker crafts `externalActionMetadata` for the LI.FI router that instructs it to pull more than `inputAmount` from the contract - up to the full unlimited allowance already set - consuming both the newly-sent `inputAmount` and the stranded residual balance.
4. `swappedAmount` (measured only around the router call) reflects proceeds from the combined amount, and the entire `amountToSendToHinkal` is packed into the attacker's single output UTXO (`utxoSet[0]`), which Hinkal accepts because Hinkal's own balance-diff check only verifies its own token accounting (`balanceDif == amountChanges[i] + utxoAmount`), not whether the action's declared output legitimately derives solely from `-deltaAmountChanges` for that tx.

Existing guards do not prevent this: `performHinkalChecks`, `verifyProof`, and the balance/slippage requires operate on Hinkal's own balances and the attacker's own UTXO commitments, not on whether the external action's router call consumed more tokens than it was given that transaction. The circuit's `inTotal + amountChanges === outTotal` constrains Hinkal's internal ledger consistency, not the external action's on-chain token flows, which are outside circuit visibility.

### Impact Explanation
The attacker captures protocol/relay fee dust (and potentially other users' stranded balances left by the same no-fee-forwarding bug) as their own shielded output UTXO, i.e., direct theft of in-flight/protocol funds from the external action contract. This is repeatable each time a zero-relay transaction strands fee dust and a subsequent attacker transaction reuses the same token as input, matching the Critical category (direct theft of shielded or in-flight user/protocol funds).

### Likelihood Explanation
Preconditions are cheap and fully attacker-controlled: submit a self-relayed (`relay == address(0)`) swap to create dust (or wait for such a legitimate transaction to occur), then submit a second transaction using the same token as input with custom LI.FI calldata. No privileged role is required; `externalActionMetadata` is entirely attacker-supplied and forwarded verbatim to the router. The unlimited approval persists indefinitely once granted, making the window of exploitability arbitrarily wide.

### Recommendation
- Do not leave fee amounts stranded when `relay == address(0)`: either forward `totalFee` back to Hinkal/the user, or skip the fee deduction entirely when no relay is present.
- Replace `approveUnlimited` with an approve-then-reset-to-exact-amount pattern scoped tightly to `inputAmount` for each call, so no exploitable residual allowance survives between transactions.
- Consider tracking and periodically sweeping/crediting any pre-existing balance in the action contract at the start of `swap`, and bound the router call's ability to consume more than `inputAmount` (e.g., verify input-token balance decreased by exactly `inputAmount`).

### Proof of Concept
Foundry plan:
1. Deploy `LifiExternalAction` with a mock router that performs `transferFrom(action, router, amountEncodedInCalldata)` then credits an output token 1:1.
2. Perform transaction A through Hinkal with `circomData.relay == address(0)`, `feeStructure.flatFee > 0`/`variableRate > 0`, and `outputToken == feeToken`; assert `outputToken.balanceOf(action) == totalFee` after the tx (dust stranded).
3. Perform transaction B where `inputToken == outputToken` from step 2, `deltaAmounts[0] == -inputAmount` (attacker's own legit deposit), but craft the mock router calldata to pull `inputAmount + totalFee` from the action contract via the still-outstanding allowance.
4. Assert `utxoSet[0].amount` (and thus `amountToSendToHinkal`) reflects the swap of `inputAmount + totalFee`, i.e., strictly greater than what corresponds to `-deltaAmounts[0]` for transaction B, and that `outputToken.balanceOf(action) == 0` after transaction B (all dust captured by the attacker's UTXO).
5. Assert the equality `tokens leaving action in tx B == -deltaAmountChanges[tx B]` fails (LHS includes the stolen dust, RHS does not).

### Citations

**File:** contracts/external-actions/swaps/ExternalActionSwap.sol (L70-93)
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

        uint256 totalFee = hinkalFee +
            (outputToken == circomData.feeStructure.feeToken ? relayFee : 0);
        uint256 amountToSendToHinkal = swappedAmount - totalFee;

        transferERC20TokenOrETH(outputToken, msg.sender, amountToSendToHinkal);
```

**File:** contracts/Transferer.sol (L178-190)
```text
    function sendToRelay(
        address relay,
        uint256 actualAmount,
        address erc20TokenAddress
    ) internal {
        if (relay != address(0) && actualAmount > 0) {
            transferERC20TokenOrETH(
                erc20TokenAddress,
                relay,
                uint256(actualAmount)
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
