### Title
Small partial fills round to zero escrow release in `IntrinsicIntents._fillSameChain` — ([File: evm/src/apps/intentsv2/IntrinsicIntents.sol])

### Summary
The same-chain intent-fill path computes the escrowed input tokens released to a partial-fill solver using integer division: `escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired`. When `order.inputs[i].amount` (the escrowed input) is small relative to `totalRequired` (the total required output), any partial fill that is not the exact completing fill can truncate to zero, so the solver delivers real output tokens to the beneficiary but is compensated with zero escrowed input — the same integer-division "zero shares" class of bug as the referenced `InsuranceFund.depositFor` report.

### Finding Description
In `_fillSameChain`: [1](#0-0) 

The escrow-release amount for a partial fill is only computed via the special full-completion branch (`amountFilled == totalRequired`, which correctly releases the *entire* remaining escrow balance, avoiding dust loss on the last fill). Every non-completing partial fill instead uses:
```
escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
```
This is standard Solidity integer division and truncates toward zero. If `order.inputs[i].amount` (the escrowed input amount for that token) is small enough relative to `totalRequired` — e.g. the input token has few decimals, the order's fee-reduced input is a dust amount, or `totalRequired` is denominated in a high-decimal token — a solver's `fillAmount` can satisfy `fillAmount * order.inputs[i].amount < totalRequired`, producing `escrowedAmount == 0`.

Crucially, the function still:
- transfers `beneficiaryTotal` (the solver's real output tokens) to the beneficiary via `safeTransferFrom`/native transfer [2](#0-1) 
- advances `_partialFills[commitment][outputToken]` to record the fill as consumed [3](#0-2) 
- emits `PartialFill` and calls `_withdraw` with `escrowedAmount = 0` for that solver [4](#0-3) 

So the solver's output-token contribution is permanently spent (delivered to the beneficiary) while receiving nothing in return for that fill — the order's compensation for that increment is silently zeroed out. Unlike the InsuranceFund original report where the recommendation is to revert on a zero-share result, here the code does not revert or guard against `escrowedAmount == 0`; the fill is accepted and processed as a normal, "successful" partial fill.

### Impact Explanation
This is a fund-loss bug reachable by any unprivileged solver interacting with `fillOrder`/`_fillSameChain` on an order whose input/output amount ratio makes early partial fills round down to zero. A solver who does not (or cannot) fill the exact completing amount donates real value to the order's beneficiary for zero compensation. An order creator (or a colluding beneficiary) can deliberately construct orders with a tiny escrowed input amount and a large `totalRequired` output amount to bait solvers into uncompensated partial fills, extracting free output-token liquidity from any solver that fills less than the full remaining amount. This satisfies "concrete theft of funds" for solvers acting on the intents system.

### Likelihood Explanation
Likelihood is moderate-to-high: partial fills are an explicitly supported same-chain feature (`Order.output` partial fill flow documented and tested), solvers routinely fill less than the full remaining amount, and the rounding condition only requires `order.inputs[i].amount` to be small relative to `totalRequired` — easily engineered by whoever creates the order, or naturally occurring with low-decimal input tokens (e.g. 6-decimal USDC input vs 18-decimal output) combined with small remaining escrow balances late in a multi-fill sequence.

### Recommendation
Guard the non-completing branch the same way the InsuranceFund report recommends: revert (or fall back to releasing at least 1 unit / require a minimum fillAmount) when the computed `escrowedAmount` would be zero for a non-zero `fillAmount`, e.g.:
```solidity
escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
if (escrowedAmount == 0) revert InsufficientFillAmount();
```
or require `fillAmount` large enough that `fillAmount * order.inputs[i].amount >= totalRequired` before accepting a partial (non-completing) fill.

### Proof of Concept
1. User places an order with `inputs[0].amount = 100` (e.g. wei-scale escrow after fee reduction) and `output.assets[0].amount = 1_000_000e18` (large output requirement), allowing partial fills.
2. Solver A fills with `solverAmount = 1e18` (0.0001% of `totalRequired`).
   - `fillAmount = 1e18`, `escrowedAmount = (100 * 1e18) / 1_000_000e18 = 0` (truncated).
   - Solver A transfers `1e18` output tokens to the beneficiary and receives `0` escrowed input tokens.
3. This repeats for every solver that does not provide the exact remaining amount; only the solver who happens to complete the order to exactly `totalRequired` receives the (tiny) full remaining escrow via the `amountFilled == totalRequired` branch.
4. Net effect: early partial-fill solvers permanently lose the value of their output-token contribution with zero on-chain compensation, while `_partialFills` bookkeeping accepts the fill as valid (no revert).

### Citations

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L91-92)
```text
            uint256 amountFilled = alreadyFilled + fillAmount;
            _partialFills[commitment][outputToken] = amountFilled;
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L95-106)
```text
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
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L111-118)
```text
            uint256 escrowedAmount;
            if (amountFilled == totalRequired) {
                escrowedAmount = _orders[commitment][address(uint160(uint256(order.inputs[i].token)))];
            } else {
                escrowedAmount = (order.inputs[i].amount * fillAmount) / totalRequired;
            }
            escrowedInputs[i] = TokenInfo({token: order.inputs[i].token, amount: escrowedAmount});
            outputFills[i] = TokenInfo({token: outputToken, amount: fillAmount});
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L126-129)
```text
        WithdrawalRequest memory body = WithdrawalRequest({
            commitment: commitment, tokens: escrowedInputs, beneficiary: bytes32(uint256(uint160(msg.sender)))
        });
        _withdraw(body, false, isFullyFilled);
```
