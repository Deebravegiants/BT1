Confirmed: there is no token whitelist restricting `IntentGatewayV2` input tokens, so any ERC20 (including rebasing tokens like stETH) can be used as an order input. This is analogous to the reported bug and reachable by an unprivileged user placing an order.### Title
Rebasing/negative-yield ERC20 escrow tokens can permanently freeze other users' orders in `IntentGatewayV2` - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2`/`IntentsBase` escrows arbitrary ERC20 tokens supplied by an unprivileged user via `placeOrder`, recording the escrowed amount as a fixed point-in-time integer in the `_orders[commitment][token]` mapping. There is no token whitelist restricting which ERC20 can be used as an order input. `_withdraw` later transfers exactly that recorded integer amount out of the contract's token balance, with no check against the contract's *actual* current `balanceOf`. If the escrowed token is a rebasing token whose balance can decrease independently of transfers (e.g. Lido's stETH under a slashing/negative-yield event, or any negative-rebasing token), the sum of outstanding `_orders[...]` accounting entries across all open orders can exceed the contract's real token balance, causing later `safeTransfer` calls in `_withdraw` to revert and permanently freeze funds for the affected orders (fill, cancel, and refund all route through `_withdraw`).

### Finding Description
`placeOrder` computes the escrowed amount from an actual balance delta at deposit time (correctly handling fee-on-transfer tokens), then stores it as a static integer:

```solidity
// evm/src/apps/IntentGatewayV2.sol:364-373
for (uint256 i; i < inputsLen;) {
    address token = address(uint160(uint256(order.inputs[i].token)));
    if (_orders[commitment][token] != 0) revert InvalidInput();
    _orders[commitment][token] = reducedInputs[i].amount;
    ...
}
```

This value is treated as a fixed liability throughout the order's lifecycle. Later, `_withdraw` (used for `RedeemEscrow`, `RefundEscrow`, same-chain fills, and same-chain cancels) decrements this fixed accounting value and transfers exactly that amount, regardless of the contract's actual token balance:

```solidity
// evm/src/apps/intentsv2/IntentsBase.sol:451-470
function _withdraw(WithdrawalRequest memory body, bool isRefund, bool finalize) internal {
    ...
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

Unlike Pods Finance's `DepositQueueLib`, which tracks a single vault's deposit against one rebasing asset, `IntentGatewayV2` is a shared escrow pool that simultaneously holds many *different, unrelated* orders' tokens in the same contract balance for the *same* token address. There is no per-token whitelist or restriction preventing users from using rebasing/slashing-exposed tokens (e.g., stETH) as `order.inputs[i].token`, and there is no mechanism to reconcile the aggregate `_orders` accounting against the actual `balanceOf(address(this))` for that token. If the token experiences a negative rebase (balance decrease independent of transfers) between deposit and settlement — for any one of potentially many concurrently escrowed orders in that token — the contract's true balance for that token falls below the sum of all outstanding `_orders[...][token]` entries. The first orders to be withdrawn (filled/cancelled/refunded) succeed by draining a disproportionate share of the shrunken balance, while later orders' `_withdraw` calls revert with insufficient balance, since `safeTransfer` will fail. Because `_withdraw` is the single code path used by `RedeemEscrow`, `RefundEscrow`, `_fillSameChain`, and `_cancelSameChain` alike, those later orders cannot be filled, cancelled, or refunded — their escrowed funds become permanently stuck (the gateway holds insufficient balance to ever satisfy them, and there is no rescue/re-credit mechanism visible in this contract, unlike Pods Finance's stated manual "top up the vault" mitigation, which has no analog here since Hyperbridge is a permissionless multi-order shared pool, not a single-owner vault).

### Impact Explanation
This is a permanent freezing-of-funds vulnerability reachable by any unprivileged user who places an order using a negative-rebasing ERC20 as an input token (`placeOrder` in `IntentGatewayV2.sol` / `IntentsBase`/`IntrinsicIntents`/`ExtrinsicIntents`). Because the gateway pools escrow for the same token address across many independently-created orders, a rebase event affecting the shared balance can cause a subset of otherwise-legitimate orders to become permanently unwithdrawable — their escrowed principal is trapped with no available recovery path in the contract logic. This meets the "permanent freezing of funds" impact bar.

### Likelihood Explanation
Likelihood is Medium: it requires (a) a user or attacker choosing/being permitted to escrow a rebasing/slashing-exposed token (no whitelist prevents this) and (b) a negative rebase event occurring on that token while multiple orders using it are concurrently outstanding in the gateway. This is not an everyday occurrence for most ERC20s, but is a known, real, and recurring risk specifically for widely-used liquid staking tokens (stETH) and similar yield-bearing assets, which are attractive intent-input assets. An attacker could also deliberately front-run this by placing many low-value orders in a token about to undergo negative rebasing (or a malicious/rug-style rebasing token) to grief victims into stuck escrow.

### Recommendation
Track escrowed balances in shares/units of the underlying rebasing token (analogous to Lido's `stETH` share mechanics) rather than static point-in-time balance amounts, or alternatively measure and transfer based on the contract's actual current `balanceOf` proportionally reconciled against outstanding `_orders` liabilities before executing any transfer in `_withdraw`. At minimum, maintain a per-token whitelist that excludes known rebasing/slashing-exposed tokens from being used as intent inputs, or isolate escrow accounting per-order using segregated custody (e.g., per-order transient escrow contracts) instead of a shared pooled balance across concurrent orders for the same token.

### Proof of Concept
1. Deploy `IntentGatewayV2` with no token restrictions (as in current code — confirmed no whitelist logic exists in `evm/src/apps/**`).
2. User A calls `placeOrder` with `order.inputs[0].token = stETH`, amount `X`; gateway records `_orders[commitmentA][stETH] = X` and holds `X` stETH.
3. User B calls `placeOrder` with `order.inputs[0].token = stETH`, amount `Y`; gateway records `_orders[commitmentB][stETH] = Y` and now holds `X + Y` stETH.
4. A Lido slashing/negative-rebase event occurs, reducing the gateway's actual stETH balance to `< X + Y` (e.g., down to `X + Y - Δ`).
5. User A's order is cancelled/filled first; `_withdraw` calls `IERC20(stETH).safeTransfer(beneficiary, X)`, succeeding and leaving the gateway with `Y - Δ` stETH.
6. User B's order is then cancelled/filled; `_withdraw` calls `IERC20(stETH).safeTransfer(beneficiary, Y)`, which reverts because the contract's actual balance (`Y - Δ`) is less than `Y`. User B's escrow is now permanently stuck — every code path that leads to `_withdraw` (`RedeemEscrow`, `RefundEscrow`, same-chain fill, same-chain cancel) for commitment B will revert identically, since `_orders[commitmentB][stETH]` still records the un-rebased `Y`.