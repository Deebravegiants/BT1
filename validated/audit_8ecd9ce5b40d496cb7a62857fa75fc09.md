### Title
Ledger-based escrow accounting in `IntentGatewayV2`/`IntentsBase._withdraw` is incompatible with rebasing/dynamically-balanced ERC20 tokens, enabling permanent freezing of escrowed funds - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentGatewayV2` escrows ERC20 input tokens for many concurrent orders in a single shared contract, tracking each order's entitlement purely in the `_orders[commitment][token]` ledger. Withdrawals (fills, cancellations, cross-chain refunds/redemptions) transfer the *ledger-recorded* amount rather than re-deriving it from the contract's actual live `balanceOf`. If an escrowed token's balance can change automatically outside of `transfer`/`transferFrom` calls (e.g. a rebasing, fee-bearing, or interest/share token such as `wibBTC`), the gateway's real token balance can silently diverge below the sum of all outstanding ledger entries, causing later withdrawers to be unable to redeem their full recorded escrow — a direct analog to the reported Curve StableSwap/`wibBTC` balance-desync issue.

### Finding Description
`IntentGatewayV2` does correctly handle *transfer-time* balance deviations (fee-on-transfer tokens) by measuring `balanceOf` before/after each transfer at `placeOrder` time and mutating `order.inputs[i].amount` to the actually-received value, as seen in `placeOrder`: [1](#0-0) 

However, once tokens are escrowed, the `_orders` ledger is treated as authoritative for the lifetime of the order, which can span the entire `deadline` window plus additional cross-chain round trips for cancellation/refund: [2](#0-1) 

All release paths — same-chain fill/cancel, cross-chain `RedeemEscrow`, and cross-chain `RefundEscrow` — funnel through `_withdraw`, which transfers exactly the ledger's recorded `amount` and decrements the ledger by that same amount, without ever re-checking the contract's actual current `balanceOf(token)`: [3](#0-2) 

Because many different orders' escrows for the same token address accumulate in this one shared contract balance (there is no per-order token custody, only a per-order ledger entry against a common pool), the model implicitly assumes `IERC20(token).balanceOf(address(this)) == sum(_orders[*][token])` holds at all times after placement. This assumption breaks for any ERC20 whose balance changes automatically without an explicit `transfer` — e.g. a wrapped, interest/rebasing, or auto-compounding token analogous to `wibBTC`, where the pricePerShare/balance can decrease (negative rebase, slashing-based yield token, or an automatic fee-skim token) while sitting in the gateway's custody. Once the actual balance drops below the ledger total, `IERC20(token).safeTransfer(beneficiary, amount)` in `_withdraw` will revert for whichever withdrawal is attempted once the shortfall is reached, since the ledger still promises the pre-rebase amount to every remaining order.

### Impact Explanation
Because escrow is pooled across all concurrent orders for a given token rather than isolated per order, a balance shortfall caused by one rebasing/dynamic-balance token affects every other order sharing that token in escrow at that time, not just the order whose underlying asset rebased. Once the real balance is insufficient, `_withdraw`'s `safeTransfer` reverts for the affected order(s), and since the ledger doesn't reflect the new "real" total, there is no self-healing path (no `sync()`-like function is exposed) — the affected users' escrowed inputs become permanently unrecoverable through fill or cancellation, i.e. a freezing of funds. This mirrors the original report's finding that Curve's ledger-based reserve tracking cannot reconcile with `wibBTC`'s dynamic balance, except here the consequence is direct fund lock rather than mispriced swaps.

### Likelihood Explanation
This requires the deployment/governance to register (via `TokenGovernor`/`createAssetMapping` or direct owner configuration) an input token that is rebasing or otherwise auto-adjusts holder balances without transfers — not all ERC20s, but a realistic and common category (liquid-staking/yield-bearing wrappers, some interest-bearing vault shares). Given the Intent Gateway is explicitly designed as a generic multi-token escrow accepting arbitrary caller-specified `TokenInfo.token` addresses in `placeOrder`, and orders can remain escrowed for extended windows (`deadline`, cross-chain round trips), the likelihood of an integrator or user selecting such a token, intentionally or not, is credible, especially since the fee-on-transfer handling already present suggests exotic ERC20 support was anticipated but only for transfer-time deviations, not custody-time ones.

### Recommendation
- Avoid pooling escrow for a given token: either isolate custody per commitment (e.g. minimal proxy/vault per order) or reconcile against live `balanceOf` at withdrawal time.
- At minimum, maintain a running invariant check: before each `_withdraw` transfer, cap the transferred amount to `min(ledgerAmount, balanceOf(address(this)))` and emit an event/flag on shortfall so it can be resolved via governance rather than silently reverting/locking funds.
- Document and, if possible, enforce (via an allowlist or a rebasing-detection check at asset-registration time) that only tokens with balances that change exclusively through `transfer`/`transferFrom`/`mint`/`burn` calls are eligible for use as `IntentGatewayV2` inputs.

### Proof of Concept
1. Governance registers a rebasing token `R` (analogous to `wibBTC`) as a valid Intent Gateway input asset.
2. Alice places `orderA` escrowing `100 R`; Bob places `orderB` escrowing `100 R` in the same `IntentGatewayV2` contract, so the contract's actual `R` balance is `200 R`, matching `_orders[A][R] + _orders[B][R] = 200`.
3. `R` undergoes a negative rebase (e.g. underlying yield-source slashing/withdrawal-fee event unrelated to any `transfer`), so the gateway's actual `balanceOf(gateway)` for `R` drops to `150 R`, while `_orders[A][R]` and `_orders[B][R]` remain `100` each (ledger unaware of the rebase).
4. Alice successfully cancels `orderA`; `_withdraw` calls `IERC20(R).safeTransfer(alice, 100)`, succeeding because `150 >= 100`; gateway's real balance falls to `50 R`. `_orders[A][R]` is zeroed as intended.
5. Bob attempts to cancel/fill `orderB`; `_withdraw` calls `IERC20(R).safeTransfer(bob, 100)`, which reverts because the gateway only holds `50 R`. Bob's escrow is now permanently unrecoverable — `_orders[B][R]` still records `100` but no on-chain function can top up the missing balance, and every future withdrawal attempt reverts identically.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L292-306)
```text
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 received;
                if (token == address(0)) {
                    received = address(this).balance - balancesBefore[i];
                } else {
                    received = IERC20(token).balanceOf(address(this)) - balancesBefore[i];
                }

                if (received > order.inputs[i].amount) {
                    uint256 dust = received - order.inputs[i].amount;
                    emit DustCollected(token, dust);
                } else {
                    order.inputs[i].amount = received;
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

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L451-470)
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
        }
```
