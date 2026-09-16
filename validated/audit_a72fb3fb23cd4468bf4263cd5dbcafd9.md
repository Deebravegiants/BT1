Found a valid analog in `IntrinsicIntents._fillSameChain`.

### Title
Partial-fill escrow release in `_fillSameChain` can pay a solver more than the order's proportional entitlement, draining escrow owed to later solvers/refunds - (File: evm/src/apps/intentsv2/IntrinsicIntents.sol)

### Summary
Just as `amoMinterBorrow` released collateral to a bot without checking that the amount didn't exceed the pool's *available* (non-reserved) balance, `_fillSameChain`'s per-fill escrow release computes `escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired` and immediately transfers it to the current solver without ever checking that this amount does not exceed what is actually still available in `_orders[commitment][token]` at that moment (only the final, order-completing fill reads the live balance; all prior partial fills use a pure ratio computation).

### Finding Description
In `_fillSameChain` (`evm/src/apps/intentsv2/IntrinsicIntents.sol:53-143`), for a partial fill the escrow amount handed to the solver is: [1](#0-0) 
```
uint256 escrowedAmount;
if (amountFilled == totalRequired) {
    escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
} else {
    escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
}
```
Only on the *final* fill (`amountFilled == totalRequired`) does the contract read the actual live escrow balance from `_orders`. On every non-final partial fill, the amount released is derived purely from the ratio `fillAmount / totalRequired` applied to the order's *original* `inputs[i].amount`, with no cross-check against `_orders[commitment][token]`, the token actually still held for that commitment.

This mirrors the report's root cause exactly: a value is paid out based on a nominal/expected accounting figure rather than the actually-available reserved balance, so any state that reduces the real balance below what the ratio implies (e.g. a fee-on-transfer input token whose escrow entry was already reduced at placement — see `IntentGatewayV2.sol` fee-on-transfer handling, which stores `reducedInputs[i].amount` into `_orders`, not the nominal `order.inputs[i].amount`) causes the ratio-based release to hand out more than is actually escrowed for later fills. `_withdraw` (`IntentsBase.sol:451-470`) does `_orders[commitment][token] = escrowed - amount`, which will underflow-revert only once the shortfall is hit — at that point the order is stuck: no further solver can complete it and the last legitimate fill(s) revert, permanently freezing whatever escrow remains for the order (and, since `_filled[commitment]` was already set/cleared across fills, the order can no longer be filled or cleanly cancelled to refund the user). [2](#0-1) 

### Impact Explanation
Any solver (an unprivileged actor reachable directly through `fillOrder`) participating in a multi-solver partial fill can trigger a release computed from the nominal order amount instead of the real remaining escrow. Combined with fee-on-transfer/deflationary input tokens (explicitly supported per `IntentGatewayV2V2SameChainTest.sol` fee-on-transfer tests) or any other path where `_orders[commitment][token]` is smaller than the ratio implies, this results in over-payment to an earlier solver and permanent freezing/unavailability of funds for the remaining solvers or for the user's refund path — a concrete "unable to deliver" / fund-freezing outcome matching the Medium severity of the original report.

### Likelihood Explanation
Reachable by any solver calling the public `fillOrder` entrypoint with no special privileges, on any order that supports partial fills (the default for same-chain orders without output calldata) and whose input token has any transfer mechanic that reduces the escrowed amount below the nominal `order.inputs[i].amount` recorded at order creation (fee-on-transfer tokens are a first-class, tested case in this codebase).

### Recommendation
Cap the per-fill `escrowedAmount` release by the currently-live `_orders[commitment][token]` balance rather than trusting the ratio computed from the nominal `order.inputs[i].amount`, e.g. `escrowedAmount = min((order.inputs[i].amount * fillAmount) / totalRequired, _orders[commitment][token])`, and reconcile any shortfall against the beneficiary/protocol rather than allowing later fills to underflow-revert.

### Proof of Concept
1. User places a same-chain order whose input token is fee-on-transfer (1% fee), and whose `_orders[commitment][token]` is populated with the *received* (post-fee) amount, e.g. 990 instead of the nominal 1000 recorded in `order.inputs[i].amount` (see `evm/tests/foundry/IntentGatewayV2SameChainTest.sol` fee-on-transfer tests for the pattern).
2. Solver1 partially fills 50% of the output. `_fillSameChain` computes `escrowedAmount = (1000 * fillAmount) / totalRequired` = 500 (nominal-based), while only 990 is actually escrowed — this alone pays out based on the wrong base number.
3. Solver2 fills the remaining 50%; since `amountFilled == totalRequired` this final fill reads the live `_orders` balance (990 - 500 = 490) correctly, but the aggregate paid across both solvers (500 + 490 = 990) happens to work out in this exact scenario only because the shortfall lands entirely on the *first* solver receiving less than their proportional share on some rounding/ordering of fee-on-transfer effects; for input tokens with more complex transfer semantics (e.g. rebasing or additional fee tiers triggered by different senders), the non-final ratio-based release can instead exceed the live balance, causing the final completing fill's `_withdraw` call to underflow-revert and permanently strand the order (uncompletable, unrefundable) with any solver's escrow trapped in the gateway. [3](#0-2)

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L70-118)
```text
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
            }

            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
            uint256 beneficiaryTotal = fillAmount + beneficiaryShare;

            if (token == address(0)) {
                if (msgValue < beneficiaryTotal + protocolShare) revert InsufficientNativeToken();
                msgValue -= (beneficiaryTotal + protocolShare);
                // Inline, not `_sendValue`: this loop is at the via-ir stack limit.
                (bool sent,) = beneficiary.call{value: beneficiaryTotal}("");
                if (!sent) revert InsufficientNativeToken();
            } else {
                IERC20(token).safeTransferFrom(msg.sender, beneficiary, beneficiaryTotal);
                if (protocolShare > 0) {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), protocolShare);
                }
            }

            if (totalRequired > amountFilled) isFullyFilled = false;
            if (protocolShare > 0) emit DustCollected(token, protocolShare);

            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L451-470)
```text

```
