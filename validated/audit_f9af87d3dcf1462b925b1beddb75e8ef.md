### Title
`swap_debt` applies the borrow-position limit to the new debt slot before the old debt is repaid, permanently blocking debt refinancing for accounts at `max_borrow_positions` - ([File: contracts/controller/src/strategies/swap_debt.rs](contracts/controller/src/strategies/swap_debt.rs))

### Summary
Analogous to the Astaria `buyoutLien` bug (the `maxLiens` check lived in `_createLien`, which also served lien replacement), the borrow-position count check in XOXNO Lending lives in `borrow_into_controller`, which `swap_debt` calls *before* it repays the existing debt. An account at `max_borrow_positions` that wants to move debt from asset A to a new asset B always reverts with `PositionLimitExceeded`, even when the swap would fully repay A and leave the net position count unchanged — the same "replace counted as append" defect.

### Finding Description
`process_swap_debt` executes in this order:

1. `borrow_into_controller(...)` for `new_debt` [1](#0-0) 
2. `swap_tokens_or_passthrough` to convert proceeds into the old debt asset [2](#0-1) 
3. `repay_debt_from_controller` against `existing_debt` [3](#0-2) 

Inside `borrow_into_controller`, `validate_position_entry_gates` is invoked with `AccountPositionType::Borrow` *before* the pool borrow and long before the repayment leg [4](#0-3) . That gate calls `validate_bulk_position_limits`, which counts `current_count + new_positions_count <= max_allowed` and reverts with `CollateralError::PositionLimitExceeded` [5](#0-4) . Because `existing_debt != new_debt` is enforced (`AssetsAreTheSame`) [6](#0-5) , the new debt is always a not-yet-held slot, so `current_count = max_borrow_positions` plus one new slot always fails — even though the subsequent `repay_debt_from_controller` leg can fully close the old slot and return the account to the cap.

The documentation itself concedes the ordering: "The new borrow must fit its borrow cap and the borrow-position limit before repayment" [7](#0-6) . Note the asymmetry with `swap_collateral`, where a full same-slot replacement at `max_supply_positions` is tested to succeed [8](#0-7) ; no equivalent escape exists on the debt side.

### Impact Explanation
Temporary freezing of funds / denial of a core function. An account at the borrow-position cap cannot refinance debt across markets at all: `swap_debt` reverts unconditionally for any `new_debt` not already held. This is most damaging exactly when refinancing is needed — e.g., the old debt market's rate spikes, or the user needs to move debt to an asset matching incoming revenue. Workarounds require capital the user may not have: repaying the old debt first (defeats the purpose of a refinance), or a `flash_position` flow on a new account. Debt and collateral remain withdrawable/repayable, so impact is bounded to the swap path, matching the Medium severity of the original LienToken finding.

### Likelihood Explanation
Requires only that an account has `max_borrow_positions` distinct debt slots (cap is at most `POSITION_LIMIT_MAX = 5`) and wishes to refinance into a sixth asset — a routine state reachable through ordinary `borrow` calls by a single unprivileged user. No attacker action or privileged state is needed; the limit may also be lowered by governance, stranding accounts above the new cap.

### Recommendation
Mirror the fix applied to `swap_collateral`/ordinary top-ups: defer or net the borrow-position-limit check until after the repayment leg in `process_swap_debt` — i.e., evaluate the limit on the post-swap position set (subtracting `existing_debt` if it will be fully closed), or move the check so it counts only slots that remain open at `strategy_finalize` time [9](#0-8) . Alternatively, pre-compute whether the swap's maximum possible repayment (`repay_amount >= existing_pos` debt) closes the slot and exempt that case from the new-slot count.

### Proof of Concept
1. Governance configures `max_borrow_positions = N` (e.g., 1).
2. Alice supplies collateral and calls `Controller::borrow` to open debt in asset A; her account is at the cap.
3. Alice calls `Controller::swap_debt(caller=alice, account_id, existing_debt=A, amount=X, new_debt=B, swap=route B→A)` where the route fully covers A's debt.
4. `borrow_into_controller` → `validate_position_entry_gates` → `validate_bulk_position_limits` sees `current_count = 1`, one new slot (B) → `total = 2 > 1` → reverts `#109 PositionLimitExceeded` before any repayment, even though the transaction would end with exactly one debt position (B) and A fully closed — the same false-positive as `buyoutLien` reverting at `maxLiens`.

### Citations

**File:** contracts/controller/src/strategies/swap_debt.rs (L39-43)
```rust
    assert_with_error!(
        env,
        existing_debt != new_debt,
        GenericError::AssetsAreTheSame
    );
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L55-63)
```rust
    let amount_received = borrow_into_controller(
        env,
        &mut account,
        new_debt,
        new_debt_amount,
        true,
        PositionAction::SwDebtR,
        &mut cache,
    );
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L65-72)
```rust
    let repay_amount = swap_tokens_or_passthrough(
        env,
        caller,
        &new_debt.asset,
        amount_received,
        &existing_debt.asset,
        swap,
    );
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L74-85)
```rust
    repay_debt_from_controller(
        env,
        &mut account,
        &mut cache,
        caller,
        StrategyRepay {
            debt: existing_debt,
            debt_available: repay_amount,
            debt_pos: &existing_pos,
            action: PositionAction::SwDebtR,
        },
    );
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L87-87)
```rust
    strategy_finalize(env, account_id, &mut account, &mut cache);
```

**File:** contracts/controller/src/positions/debt.rs (L269-277)
```rust
    require_positive_amount(env, amount);
    let aggregated = vec![env, (hub_debt.clone(), amount)];
    validate_position_entry_gates(
        env,
        account,
        &aggregated,
        cache,
        AccountPositionType::Borrow,
    );
```

**File:** contracts/controller/src/risk/validation.rs (L104-111)
```rust
    let total_positions = current_count
        .checked_add(new_positions_count)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));
    assert_with_error!(
        env,
        total_positions <= max_allowed,
        CollateralError::PositionLimitExceeded
    );
```

**File:** docs/reference/endpoints.md (L33-33)
```markdown
| `swap_debt(caller: Address, account_id: u64, existing_debt: HubAssetKey, amount: i128, new_debt: HubAssetKey, swap: Bytes)` | NFT owner/delegate | gated | Borrow new debt, then repay existing debt with the swap output. The new borrow must fit its borrow cap and the borrow-position limit before repayment. |
```

**File:** tests/test-harness/tests/strategy/edge/rejections.rs (L228-248)
```rust
fn test_swap_collateral_full_close_frees_slot_at_max_positions() {
    let mut t = LendingTest::new()
        .three_asset_usdc_eth_wbtc()
        .with_market(usdt_stable_preset())
        .with_market(dai_preset())
        .with_position_limits(4, 4)
        .build();

    let account_id = t.create_account(ALICE);
    t.supply_to(ALICE, account_id, "USDC", 10_000.0);
    t.supply_to(ALICE, account_id, "ETH", 1.0);
    t.supply_to(ALICE, account_id, "WBTC", 0.1);
    t.supply_to(ALICE, account_id, "USDT", 5_000.0);

    t.fund_router("DAI", 10_000.0);
    let steps = build_aggregator_swap(&t, "USDC", "DAI", 100_000_000_000, 100_000_000_000);
    let result = t.try_swap_collateral(ALICE, "USDC", 10_000.0, "DAI", &steps);
    assert!(
        result.is_ok(),
        "a full same-slot swap at max positions must succeed: {result:?}"
    );
```
