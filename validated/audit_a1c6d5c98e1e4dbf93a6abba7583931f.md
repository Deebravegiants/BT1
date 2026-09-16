## Analog Found

### Title
Intent escrow accounting uses static per-order balances that don't account for rebasing tokens after deposit - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2`/`IntentsBase` already defends against fee-on-transfer tokens **at deposit time**: `placeOrder` measures the gateway's actual balance delta after `safeTransferFrom` and mutates `order.inputs[i].amount` to the amount actually received before it is written into escrow. [1](#0-0)  However, once tokens are recorded in the `_orders[commitment][token]` mapping, that nominal figure is treated as a fixed, static claim on the pooled token balance held by the contract for the lifetime of the order — there is no mechanism that reconciles it against the actual `balanceOf(this)` if the escrowed token rebases (up or down) while sitting in escrow. `_withdraw` releases exactly the recorded nominal amount via `safeTransfer`, regardless of the contract's real balance at redemption time. [2](#0-1) 

### Finding Description
The gateway pools escrow for many concurrent orders in the same ERC-20 contract balance; `_orders[commitment][token]` is a nominal bookkeeping entry, not a segregated balance. [3](#0-2)  If the underlying token is a rebasing asset (balance mutates without a `transfer` call, e.g. positive/negative rebases), the sum of all outstanding `_orders[...][token]` entries can drift away from the token's actual `balanceOf(address(this))`:

- A rebase **down** shrinks the real balance without shrinking any `_orders` entry. Whichever order is redeemed first via `_withdraw` still pulls its full nominal `escrowed` amount with `IERC20(token).safeTransfer(beneficiary, amount)`, leaving strictly less real balance for orders redeemed later — some of which can then fail (`safeTransfer` reverting due to insufficient balance), permanently freezing that order's escrow.
- A rebase **up** grows the real balance without crediting any order; the surplus is unaccounted for by any `_orders` entry, and unlike protocol fee dust (which is captured via `DustCollected` at deposit-time only, e.g. [4](#0-3) ), post-deposit rebase gains are never swept or attributed and are effectively grabbed by whichever party interacts with the escrow accounting incidentally (or stranded).

This is the same root-cause pattern as the reported Curve issue: a pooled balance backing multiple independent claims is tracked with static, per-claim nominal accounting that assumes the underlying asset balance is 1:1 stable, so whichever claim is settled first can unfairly benefit or unfairly starve claims settled later once the token's balance diverges from the sum of recorded claims.

### Impact Explanation
For any deployment where `IntentGatewayV2` accepts a rebasing ERC-20 as an input/output token, concurrently-escrowed orders sharing that token's pooled balance can have their redemption/refund permanently blocked (frozen funds) once a downward rebase occurs before settlement, because `_withdraw` unconditionally attempts to transfer the full nominal `escrowed` amount out of a balance that may no longer contain it. This is reachable by ordinary flow: any user's `placeOrder`, any solver's `fillOrder`, or any relayer delivering a `RedeemEscrow`/`RefundEscrow` cross-chain message via `onAccept` — no privileged role is required to trigger the divergence or to be the party harmed by it.

### Likelihood Explanation
Likelihood is low-to-medium, matching the referenced report's own MEDIUM severity rationale: rebasing tokens are a minority of ERC-20s that a gateway operator could list as inputs/outputs, and the accounting only diverges once the token's supply/balance mechanics change while multiple orders share exposure to the same token pool between `placeOrder` and settlement. This mirrors the analog's premise that "slashings/rebases are rare events" but the missing accounting still creates unfair outcomes when they occur.

### Recommendation
Document explicitly (as the original report recommends for `_balances`) that `_orders` escrow accounting in `IntentsBase.sol` assumes standard, non-rebasing ERC-20 tokens once inside escrow — the fee-on-transfer handling in `placeOrder` only reconciles the deposit-time delta, not ongoing rebases. Either add this restriction to gateway token-listing policy/documentation, or make `_withdraw` bound each release by the contract's live `balanceOf` for that token so a downward rebase degrades proportionally across outstanding orders instead of letting earlier redemptions fully drain the shrunk balance at later redeemers' expense.

### Proof of Concept
1. Deploy `IntentGatewayV2` with a rebasing ERC-20 `R` as the input token.
2. User A places `orderA` escrowing `1000 R` (`_orders[commitmentA][R] = 1000`); User B places `orderB` escrowing `1000 R` in the same block window (`_orders[commitmentB][R] = 1000`). Gateway `balanceOf(R) == 2000`.
3. `R` undergoes a negative rebase, shrinking the gateway's `balanceOf(R)` to `1200` without touching `_orders` entries (still `1000` each).
4. Solver fills `orderA`; `_withdraw` decrements `_orders[commitmentA][R]` to `0` and calls `safeTransfer(solverA, 1000)` — succeeds, leaving gateway with `200 R`.
5. Solver attempts to fill `orderB`; `_withdraw` reads `escrowed = 1000`, calls `safeTransfer(solverB, 1000)` against a `200 R` balance — reverts, permanently freezing `orderB`'s escrow (and its counterpart on the destination chain, since the cross-chain redeem message cannot complete). [5](#0-4)

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L301-306)
```text
                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
                }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L318-323)
```text
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L140-144)
```text
    /**
     * @dev Maps (commitment, token address) to the escrowed amount for that token.
     * Decremented as tokens are released via fills or refunds.
     */
    mapping(bytes32 => mapping(address => uint256)) public _orders;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-469)
```text
    function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
        address beneficiary = address(uint160(uint256(body.beneficiary)));
        if (finalize) _filled[body.commitment] = beneficiary;

        uint256 len = body.tokens.length;
        for (uint256 i; i < len; i++) {
            address token = address(uint160(uint256(body.tokens[i].token)));
            uint256 amount = body.tokens[i].amount;
            if (amount == 0) continue;

            uint256 escrowed = _orders[body.commitment][token];
            if (escrowed == 0) revert UnknownOrder();

            _orders[body.commitment][token] = escrowed - amount;
            if (token == address(0)) {
                _sendValue(beneficiary, amount);
            } else {
                IERC20(token).safeTransfer(beneficiary, amount);
            }
```
