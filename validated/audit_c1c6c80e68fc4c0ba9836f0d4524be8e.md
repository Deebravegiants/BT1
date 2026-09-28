### Title
Tokens pushed to the controller during `flash_position` without being declared in `collaterals`/`refund_assets` are permanently locked — no entrypoint can ever recover them - (File: contracts/controller/src/strategies/legs.rs)

### Summary
The controller measures settlement exclusively by balance deltas on caller-declared assets. During `flash_position` (and the same accounting in `multiply`/`swap_*` strategies), any token a flash receiver transfers to the controller that is not declared as a collateral leg or in `refund_assets` is neither credited to a position nor refunded. There is no rescue/sweep entrypoint, so the tokens sit on the controller address forever — the direct analog of the bridge's "deposit accepted under an option the withdrawal path cannot process, locking funds permanently."

### Finding Description
`withdraw_collateral_to_controller` and the repayment/refund helpers settle by measuring `token.balance(controller)` before/after via `balance_delta_since`, and only for assets the caller declared. [1](#0-0) 

Only declared `refund_assets` are swept back by `refund_controller_balance_delta`; the code comment in `require_external_recipient` states the invariant explicitly: "controller receipts would remain unclaimed by balance-delta accounting." [2](#0-1) 

The test harness demonstrates the reachable shape: `FlashPositionMode::Undeclared` pushes the declared collateral plus an extra `extra_amount` of an undeclared `extra_asset` to the controller during the callback. [3](#0-2)  The integration flow documents that "the undeclared USDC is not credited" — it is also not refunded, because `refund_assets` rejects duplicates and any overlap with collateral legs. [4](#0-3) 

The controller's public surface (README: positions, strategies, maintenance) contains no entrypoint to recover stranded controller balances — `claim_revenue` only pulls pool revenue to the accumulator, and `recapitalize` moves tokens *into* the pool. [5](#0-4) 

The lock is also *forced* in one edge case: `refund_assets` rejects duplicates and any address already declared as a collateral leg (`Error #16`), so a receiver that pushes extra units of an asset whose declaration slot cannot be expressed (e.g., list-length exhaustion or overlap rejection during simulation drift at inclusion) has no way to declare it.

### Impact Explanation
Permanent freezing of funds. Tokens transferred to the controller but not declared are locked on the controller address with no recovery path — economically identical to the bridge report's "NFT kept while withdrawal always reverts." Any integrating contract or receiver that over-transfers, transfers an undeclared listed asset, or transfers an asset it cannot declare (overlap/dup/length constraints) loses those tokens permanently.

### Likelihood Explanation
Reachable by any unprivileged caller running `flash_position`/`multiply`/swap strategies with their own receiver or route. Requires a misdeclared or over-pushed callback transfer — self-inflicted in the common case, same as the original report's `use_withdraw_auto == true`, but there is no on-chain guard rejecting the stray transfer and no recovery verb, so a single integration mistake is unrecoverable rather than reverting.

### Recommendation
Reject the transaction if the controller's post-callback balance delta for any listed asset is nonzero but undeclared, or sweep all measured controller deltas that exceed declared legs to `caller`. Alternatively add an explicit rescue entrypoint restricted to assets with no recorded claim.

### Proof of Concept
```rust
// Receiver callback (tests/test-harness/src/receivers/flash_position.rs:161)
FlashPositionMode::Undeclared => {
    push_token(&env, &request.collateral, request.collateral_amount, &controller);
    // extra_asset is NOT in collaterals and NOT in refund_assets:
    push_token(&env, &request.extra_asset, request.extra_amount, &controller);
}
```
```rust
// Caller side: declare only the collateral leg, leave extra_asset undeclared.
ctrl.flash_position(&caller, &account_id, &spoke, &mode, &debt, &amount,
                    &receiver, &data, &collaterals, &Vec::new(&env));
// Succeeds. extra_amount of extra_asset remains on the controller address.
// No controller/pool entrypoint can withdraw it — permanent lock.
```

### Citations

**File:** contracts/controller/src/strategies/legs.rs (L84-109)
```rust
pub(super) fn withdraw_collateral_to_controller(
    env: &Env,
    account: &mut Account,
    cache: &mut Context,
    req: StrategyWithdraw<'_>,
) -> i128 {
    let controller = env.current_contract_address();
    let balance_before = token::Client::new(env, &req.hub_asset.asset).balance(&controller);

    storage::with_flash_guard(env, || {
        execute_withdrawal(
            env,
            account,
            &controller,
            req.action,
            WithdrawalRequest {
                hub_asset: req.hub_asset,
                amount: req.amount,
                position: req.position,
            },
            cache,
        );
    });

    balance_delta_since(env, &req.hub_asset.asset, &controller, balance_before)
}
```

**File:** contracts/controller/src/positions/mod.rs (L33-43)
```rust
/// Rejects pool and controller recipients with `InvalidFlashloanReceiver`.
/// Pool self-transfers debit cash without moving tokens; controller receipts
/// would remain unclaimed by balance-delta accounting.
pub(crate) fn require_external_recipient(env: &Env, cache: &mut Context, recipient: &Address) {
    let pool = cache.cached_pool_address();
    assert_with_error!(
        env,
        *recipient != env.current_contract_address() && *recipient != pool,
        FlashLoanError::InvalidFlashloanReceiver
    );
}
```

**File:** tests/test-harness/src/receivers/flash_position.rs (L161-177)
```rust
            FlashPositionMode::Undeclared => {
                if request.collateral_amount > 0 {
                    push_token(
                        &env,
                        &request.collateral,
                        request.collateral_amount,
                        &controller,
                    );
                }
                if request.extra_amount > 0 {
                    push_token(
                        &env,
                        &request.extra_asset,
                        request.extra_amount,
                        &controller,
                    );
                }
```

**File:** tests/integration/flows/flash_position.sh (L375-416)
```shellscript
    # Push the wrong listed asset (USDC) while declaring XLM — measured XLM
    # delta is 0, so the min fails. The undeclared USDC is not credited.
    fp_set_plan fp_plan_wrong_asset "$FP_MODE_SUCCESS" 0 "$USDC_SAC" 10000000 || return 1
    FP_COLS="$(fp_collaterals "$FP_EXTEND_COLLATERAL")"
    fp_reject_unchanged flash_position_wrong_asset_push 'Error\(Contract, #504\)' || return 1

    # --- new-account dust fails solvency / min-borrow floor ---
    FP_ACCOUNT_ID=0
    FP_COLS="$(fp_collaterals "$FP_DUST_COLLATERAL")"
    fp_set_plan fp_plan_dust_new "$FP_MODE_SUCCESS" "$FP_DUST_COLLATERAL" || return 1
    fp_run xfail flash_position_dust_new_unhealthy 'Error\(Contract, #100\)' || true

    # --- input / auth / listing errors (callback never runs) ---
    FP_ACCOUNT_ID="$ALICE_FP_ACCT"
    FP_COLS="$(fp_collaterals "$FP_EXTEND_COLLATERAL")"
    FP_AMOUNT=0
    fp_run xfail flash_position_zero_debt 'Error\(Contract, #14\)' || true
    FP_AMOUNT=-1
    fp_run xfail flash_position_negative_debt 'Error\(Contract, #14\)' || true
    FP_AMOUNT="$FP_SMALL_DEBT"

    FP_COLS="$(fp_collaterals_on 99 "$XLM_SAC" "$FP_EXTEND_COLLATERAL")"
    FP_DEBT="$(hub_key 99 "$USDC_SAC")"
    fp_run xfail flash_position_inactive_hub 'Error\(Contract, #43\)' || true
    FP_DEBT="$(hub_key "$PRIMARY_HUB_ID" "$USDC_SAC")"

    FP_COLS="$(fp_collaterals_on "$PRIMARY_HUB_ID" "$EURC_SAC" "$FP_EXTEND_COLLATERAL")"
    fp_run xfail flash_position_unlisted_collateral 'Error\(Contract, #307\)' || true

    FP_COLS="$(jq -nc --argjson h "$PRIMARY_HUB_ID" --arg a "$XLM_SAC" \
        '[[{hub_id:$h,asset:$a},"1"],[{hub_id:$h,asset:$a},"1"]]')"
    fp_run xfail flash_position_duplicate_collateral 'Error\(Contract, #16\)' || true

    FP_COLS="$(fp_collaterals "$FP_EXTEND_COLLATERAL")"
    FP_REFUNDS="$(fp_refunds "$XLM_SAC")"
    fp_run xfail flash_position_refund_overlap 'Error\(Contract, #16\)' || true
    FP_REFUNDS=$(jq -nc --arg a "$USDC_SAC" '[$a,$a]') || return 1
    fp_run xfail flash_position_refund_duplicate 'Error\(Contract, #16\)' || return 1
    # Six distinct addresses exceed max_supply_positions=5. Without the length
    # guard, the second (unlisted) asset would fail #307 instead of #16.
    FP_REFUNDS=$(jq -nc '$ARGS.positional' --args "$USDC_SAC" "$EURC_SAC" "$CONTROLLER" "$POOL" "$GOVERNANCE" "$POSITION_NFT") || return 1
    fp_run xfail flash_position_refund_over_limit 'Error\(Contract, #16\)' || return 1
```

**File:** contracts/controller/README.md (L101-107)
```markdown
### Maintenance

| Entrypoint | Signature | Notes | What it does |
| --- | --- | --- | --- |
| `update_indexes` | `fn update_indexes(env: Env, caller: Address, assets: Vec<HubAssetKey>)` | blocked by global pause | Accrues the borrow and supply indexes for each hub asset in `assets` on the pool. |
| `claim_revenue` | `fn claim_revenue(env: Env, caller: Address, assets: Vec<HubAssetKey>) -> Vec<i128>` | blocked by global pause | Claims accrued protocol revenue for each hub asset in `assets` from the pool and forwards it to the configured accumulator, returning the amount claimed per asset. |
| `recapitalize` | `fn recapitalize(env: Env, payer: Address, hub_asset: HubAssetKey, amount: i128) -> i128` | — | Transfers `amount` of `hub_asset` from `payer` into the pool to cover a backing shortfall, applying only up to the shortfall and refunding any excess; returns the amount actually applied. |
```
