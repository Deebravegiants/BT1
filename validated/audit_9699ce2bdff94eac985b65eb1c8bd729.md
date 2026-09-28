### Title
Users can bypass the `multiply` strategy fee through self-served `flash_position` - (File: contracts/controller/src/strategies/flash_position.rs)

### Summary
`multiply` charges the market `flashloan_fee` when minting strategy debt, while the permissionless `flash_position` entrypoint mints the same type of debt with `charge_fee=false`, forwards the full amount to a caller-selected receiver, and then deposits collateral returned by that receiver. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`process_multiply` calls `borrow_into_controller` with `charge_fee=true`, so the pool withholds the configured flash-loan fee from the borrowed proceeds. [1](#0-0) [4](#0-3) 

`process_flash_position` instead accepts a caller-selected WASM receiver and invokes its `execute_flash_position` callback after forwarding the measured borrowed amount. [5](#0-4) [6](#0-5) 

The forwarded borrow is created through `borrow_into_controller` with `charge_fee=false`, and the emitted event explicitly records `fee: 0`. [2](#0-1) [7](#0-6) 

After the callback, the controller measures collateral-token receipts, deposits them into the account, and performs final solvency checks. [3](#0-2) 

Consequently, an unprivileged user can deploy their own receiver, have it swap the full fee-free borrow into collateral, return that collateral to the controller, and obtain the same leveraged debt-and-collateral position that `multiply` creates without paying the `multiply` strategy fee. [8](#0-7) [9](#0-8) 

### Impact Explanation
Every leveraged position opened through this path avoids the strategy fee that `multiply` is designed to withhold as protocol revenue. [10](#0-9) [11](#0-10) 

The borrower also receives and can deploy the full borrowed amount rather than `amount - fee`, while still ending with ordinary account debt and collateral. [12](#0-11) [13](#0-12) 

### Likelihood Explanation
Any user can create an account with `account_id=0`, select a deployed WASM receiver they control, request a supported debt asset, and specify the collateral legs and minimum returned amounts. [14](#0-13) [15](#0-14) 

The receiver can execute the swap itself during `execute_flash_position`; the controller only requires the listed collateral balance increases and a solvent final account. [16](#0-15) 

The operation still needs sufficient pool liquidity, an enabled flash-loanable debt market, swap liquidity, and enough resulting collateral to satisfy the account’s risk limits. [17](#0-16) [18](#0-17) 

### Recommendation
Charge the same debt-funded strategy fee in `flash_position`, or restrict it to protocol-controlled receivers if fee-free leverage is intentionally reserved for specific flows. [2](#0-1) [19](#0-18) 

If `flash_position` is intended to remain fee-free, remove the equivalent fee from `multiply` or document that the router convenience path charges an optional fee rather than a mandatory protocol protection. [1](#0-0) [20](#0-19) 

### Proof of Concept
The following flow demonstrates the bypass for a user-controlled receiver:

```rust
// User calls the fee-free strategy path.
controller.flash_position(
    caller,
    0,                                  // create a user-owned account
    spoke_id,
    PositionMode::Multiply,
    debt_hub_asset,
    borrow_amount,
    attacker_receiver,
    swap_data,
    vec![(collateral_hub_asset, min_collateral_out)],
    refund_assets,
);
```

During `execute_flash_position`, the receiver swaps the full `amount_received` of the debt asset into the collateral asset and transfers at least `min_collateral_out` back to the controller. [21](#0-20) [22](#0-21) 

```rust
// Conceptual receiver callback.
fn execute_flash_position(...) {
    // `amount_received == borrow_amount`; no flashloan_fee was withheld.
    swap_debt_asset_for_collateral(amount_received);
    token::transfer(controller, collateral_asset, collateral_received);
}
```

The controller then credits the measured collateral receipt and finalizes the debt-backed position while emitting `fee: 0`. [23](#0-22)

### Citations

**File:** contracts/controller/src/strategies/multiply.rs (L76-84)
```rust
    let amount_received = borrow_into_controller(
        env,
        &mut account,
        debt,
        debt_to_flash_loan,
        true,
        PositionAction::Multiply,
        &mut cache,
    );
```

**File:** contracts/controller/src/strategies/multiply.rs (L86-110)
```rust
    let swap_amount_in = amount_received
        .checked_add(debt_extra)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    let swapped_collateral = swap_tokens_or_passthrough(
        env,
        caller,
        &debt.asset,
        swap_amount_in,
        &collateral.asset,
        swap,
    );

    let total_collateral = collateral_amount
        .checked_add(swapped_collateral)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    let deposit_assets = vec![env, (collateral.clone(), total_collateral)];
    supply::process_deposit(
        env,
        &env.current_contract_address(),
        &mut account,
        &deposit_assets,
        &mut cache,
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L69-76)
```rust
    require_wasm_receiver(env, receiver);

    let controller = env.current_contract_address();
    assert_with_error!(
        env,
        *receiver != controller,
        FlashLoanError::InvalidFlashloanReceiver
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L85-91)
```rust
    // Caller-selected receivers require flash loans enabled; multiply uses
    // the configured router and does not require this flag.
    assert_with_error!(
        env,
        cache.cached_pool_sync_data(debt).params.is_flashloanable,
        FlashLoanError::FlashloanNotEnabled
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L93-111)
```rust
    let (account_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        mode,
        account::AccountGuard::Multiply,
        &mut cache,
    );

    validate_collaterals(env, &mut cache, &account, collaterals);
    validate_refund_assets(
        env,
        &mut cache,
        account.spoke_id,
        debt.hub_id,
        collaterals,
        refund_assets,
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L120-165)
```rust
    let (amount_received, collateral_before, refund_before) =
        storage::with_flash_guard(env, || {
            let amount_received =
                mint_and_forward(env, &mut account, debt, amount, receiver, &mut cache);
            // Baselines exclude funding and forwarding; count callback receipts only.
            let collateral_before = snapshot_balances(
                env,
                &controller,
                collaterals.iter().map(|(hub_asset, _)| hub_asset.asset),
            );
            let refund_before = snapshot_balances(env, &controller, refund_assets.iter());
            invoke_receiver(
                env,
                receiver,
                caller,
                account_id,
                &debt.asset,
                amount,
                amount_received,
                &controller,
                data,
            );
            (amount_received, collateral_before, refund_before)
        });

    let deposits = collect_collateral_deposits(env, &controller, collaterals, &collateral_before);
    process_deposit(env, &controller, &mut account, &deposits, &mut cache);

    refund_listed_assets(env, caller, refund_assets, &refund_before);

    // Check before and after finalization: its LTV refresh can prune zero-scaled
    // supply, and persistence removes empty accounts.
    require_flash_position_still_open(env, &account, debt);
    strategy_finalize(env, account_id, &mut account, &mut cache);
    require_flash_position_still_open(env, &account, debt);

    FlashPositionEvent {
        account_id,
        hub_id: debt.hub_id,
        asset: debt.asset.clone(),
        receiver: receiver.clone(),
        caller: caller.clone(),
        amount,
        amount_received,
        fee: 0,
    }
```

**File:** contracts/controller/src/strategies/flash_position.rs (L271-279)
```rust
    let reported = borrow_into_controller(
        env,
        account,
        debt,
        amount,
        false,
        PositionAction::FlashPos,
        cache,
    );
```

**File:** contracts/controller/src/strategies/flash_position.rs (L285-294)
```rust
    let forwarded = transfer_amount_measured(
        env,
        &debt.asset,
        &controller,
        receiver,
        measured,
        GenericError::AmountMustBePositive,
    );
    assert_with_error!(env, forwarded > 0, GenericError::AmountMustBePositive);
    forwarded
```

**File:** contracts/pool/src/ops/strategy.rs (L53-58)
```rust
/// Computes the fee, mints debt for `action.amount`, and debits cash for
/// `amount - fee`.
///
/// The fee stays in the pool as protocol revenue via
/// [`interest::add_protocol_revenue`].
pub(crate) fn accounting(env: &Env, action: PoolAction, charge_fee: bool) -> StrategyOutcome {
```

**File:** contracts/pool/src/ops/strategy.rs (L72-82)
```rust
    let protocol_fee = Ray::from_asset(env, fee, cache.params().asset_decimals);
    interest::add_protocol_revenue(&mut cache, protocol_fee);

    let amount_to_send = amount
        .checked_sub(fee)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.debit_cash(amount_to_send);

    cache.commit();
    let mutation = cache.strategy_mutation(position, amount, amount_to_send);
```

**File:** contracts/pool/src/ops/strategy.rs (L90-100)
```rust
/// Computes the strategy fee from `flashloan_fee` bps when `charge_fee` is true;
/// returns 0 otherwise (does not consult the market flash-loan enable flag).
///
/// Panics if the fee would exceed principal when charging.
fn compute_fee(env: &Env, cache: &Cache, amount: i128, charge_fee: bool) -> i128 {
    if !charge_fee {
        return 0;
    }
    let fee = Bps::from(i128::from(cache.params().flashloan_fee)).flash_loan_fee_on(env, amount);
    assert_with_error!(env, fee <= amount, FlashLoanError::StrategyFeeExceeds);
    fee
```

**File:** interfaces/controller/src/lib.rs (L60-72)
```rust
    fn flash_position(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        mode: PositionMode,
        debt: HubAssetKey,
        amount: i128,
        receiver: Address,
        data: Bytes,
        collaterals: Vec<(HubAssetKey, i128)>,
        refund_assets: Vec<Address>,
    ) -> u64;
```

**File:** contracts/controller/src/lib.rs (L182-187)
```rust
    /// Mints `amount` of `debt` without a flash fee, forwards measured receipts
    /// and invokes the Wasm receiver's `execute_flash_position` callback.
    /// `collaterals` sets minimum controller-balance increases to deposit;
    /// listed `refund_assets` balance increases return to the caller.
    /// Returns the solvent account's id; `account_id = 0` creates it. An existing
    /// account requires owner or delegate authorization and a matching mode.
```
