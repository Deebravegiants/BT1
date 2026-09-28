### Title
Suppliers can withdraw before bad-debt socialization and concentrate the loss on remaining suppliers - (File: contracts/pool/src/ops/withdraw.rs)

### Summary
Withdrawals verify available cash, utilization, and the no-debt-without-supply invariant, but do not account for imminent bad-debt write-downs. After an account becomes publicly insolvent, a supplier in the debt market can exit at the pre-write-down supply index, then anyone can execute `liquidate` or `clean_bad_debt`, causing the remaining suppliers to absorb a disproportionately larger loss.

### Finding Description
`withdraw::accounting` resolves and burns the caller's supply shares before `gate_and_debit` runs. That gate checks `require_reserves`, optionally `require_utilization_below_max`, and `require_supply_for_debt`, but never calls `guards::require_backed_market` or otherwise discounts debt that is already unrecoverable. [1](#0-0) [2](#0-1) 

The current backing calculation treats outstanding debt at its ceiled face value until a later liquidation or cleanup burns it and reduces the supply index. [3](#0-2) [4](#0-3) 

The write-down is proportional to the supply shares still present when `apply_bad_debt_to_supply_index` executes: it divides capped bad debt by current `total_supplied_value` and lowers `supply_index`. [5](#0-4) 

The strongest reachable sequence is:

1. Attacker supplies the debt-market asset and receives supply shares.
2. A borrower becomes insolvent through a legitimate price/index change.
3. Before any liquidation or cleanup transaction executes, the attacker calls `withdraw(caller=attacker, account_id=attacker_account, withdrawals=[(debt_hub_asset, 0)], to=None)`. A zero amount requests the full position.
4. The attacker calls `liquidate` or `clean_bad_debt` on the borrower, or lets another keeper perform it.
5. The bad debt is divided among only the supply shares that did not exit.

The repository's own regression scenario demonstrates this ordering: Bob withdraws all ETH after the borrower's collateral crash but before liquidation, recovers at least his full pre-crash balance, and Carol's subsequent bad-debt loss is amplified by more than three times. [6](#0-5) 

### Impact Explanation
This is a direct loss of user funds. A supplier who exits before the write-down receives an unimpaired claim even though part of the debt backing that claim is already economically unrecoverable. Suppliers who remain in the market absorb a larger share of the same loss when the supply index is reduced. In an extreme coordinated exit, the last suppliers may bear substantially all of the bad debt despite holding only a small fraction of the original supply.

Withdrawal and liquidation are both reachable while globally paused, and liquidation/bad-debt cleanup are permissionless once their eligibility conditions hold. [7](#0-6) [8](#0-7) 

### Likelihood Explanation
Likelihood is Medium. The attacker needs an existing supply position in the same market as an account that has just become insolvent, and the withdrawal must still satisfy utilization and cash-reserve checks. No privileged access, oracle manipulation, leaked key, malformed configuration, or third-party action is required: the insolvency condition is observable on-chain, `withdraw` is available to the account owner/delegate, and the subsequent socialization path is permissionless.

The impact scales with the amount of supply that can exit before the write-down. Markets with deep liquidity relative to the insolvent debt can have many suppliers race to withdraw before liquidation; thin markets will reach the utilization or reserve boundary sooner.

### Recommendation
Make exits share the already-recognized impairment. Possible fixes include:

- Apply an account's eligible bad-debt write-down before permitting withdrawals from the affected debt market.
- Have withdrawal compute backing using a conservative estimate of pending bad debt rather than face-value outstanding debt.
- Introduce a market-level shortfall or socialization flag when a qualifying insolvent account is detected, and gate exits until cleanup runs.
- Alternatively, permit withdrawals but haircut them by the projected supply-index write-down.

The invariant should be that no supplier can materially change its share of an already-observable bad-debt loss solely by submitting `withdraw` before `liquidate`/`clean_bad_debt`.

### Proof of Concept
Let an ETH market contain 75 ETH supplied by Bob and 25 ETH supplied by Carol. Alice supplies USDC collateral and borrows ETH.

```text
supply(Bob,   bob_account,   spoke_id, [(ETH, 75 ETH)])
supply(Carol, carol_account, spoke_id, [(ETH, 25 ETH)])
supply(Alice, alice_account, spoke_id, [(USDC, collateral)])
borrow(Alice, alice_account, [(ETH, debt)], None)
```

A legitimate USDC price decrease makes `debt > collateral`. Before any liquidation call is mined:

```text
withdraw(Bob, bob_account, [(ETH, 0)], None)
```

Because amount `0` denotes a full withdrawal, Bob exits at the still-unwritten-down supply index if the post-withdraw utilization and cash checks pass. Then a permissionless caller executes:

```text
liquidate(liquidator, alice_account, [(ETH, payment)], SeizeMode::Transfer)
```

or, once residual collateral is within the dust threshold:

```text
clean_bad_debt(caller, alice_account)
```

`apply_bad_debt_to_supply_index` now divides the same bad debt across Carol's remaining 25 ETH rather than the original 100 ETH of supply. Carol therefore absorbs approximately four times the loss she would have borne if Bob had remained, while Bob recovered his full claim.

### Citations

**File:** contracts/pool/src/ops/withdraw.rs (L63-80)
```rust
    let (mut cache, position) = ops::load_leg(env, &entry.action);

    let (burned, gross_amount) = resolve_close_or_partial(&cache, entry.action.amount, position);
    // Burn first: `protocol_fee_shares` caps the fee mint at `i128::MAX - supplied`.
    let remaining = burn_position(env, &mut cache, position, burned);
    let net_transfer = withhold_liquidation_fee(
        env,
        &mut cache,
        gross_amount,
        is_liquidation,
        entry.protocol_fee,
    );

    // A footprint-only close must not add a utilization gate to same-market
    // net settlement: it burns no shares and moves no cash.
    let empty_close = position.raw() == 0 && entry.action.amount == i128::MAX;
    gate_and_debit(env, &mut cache, net_transfer, is_liquidation || empty_close);

```

**File:** contracts/pool/src/ops/withdraw.rs (L109-118)
```rust
/// Enforces reserve, utilization, and solvency guards, then debits cash for
/// the net transfer. Liquidations and footprint-only closes skip utilization.
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
```

**File:** contracts/pool/src/guards.rs (L60-66)
```rust
/// Asset units by which supplier claims exceed cash + debt (0 if solvent).
pub(crate) fn backing_shortfall(cache: &Cache) -> i128 {
    let supplied_claim = cache.unscale_supply_floor(cache.supplied());
    let outstanding_debt = cache.unscale_borrow_ceil(cache.borrowed());
    let backing = cache.cash().saturating_add(outstanding_debt);
    supplied_claim.saturating_sub(backing).max(0)
}
```

**File:** contracts/pool/src/ops/seize.rs (L23-28)
```rust
    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
```

**File:** contracts/pool/src/interest.rs (L73-89)
```rust
pub(crate) fn apply_bad_debt_to_supply_index(cache: &mut Cache, bad_debt: Ray) {
    let total_supplied_value = cache.supplied().mul(cache.env(), cache.supply_index());

    if total_supplied_value == Ray::ZERO {
        return;
    }

    let capped = bad_debt.min(total_supplied_value);
    let remaining = total_supplied_value.checked_sub(cache.env(), capped);

    let reduction_factor = remaining.div_floor(cache.env(), total_supplied_value);
    let new_supply_index = cache
        .supply_index()
        .mul_floor(cache.env(), reduction_factor);

    cache.set_supply_index(new_supply_index.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW)));
}
```

**File:** tests/test-harness/tests/controller/bad_debt_index.rs (L402-473)
```rust
fn supplier_can_exit_ahead_of_bad_debt_writedown() {
    // Scenario A: nobody dodges. Bob 75%, Carol 25% of the ETH supply.
    let mut a = setup();
    a.supply(BOB, "ETH", 75.0);
    a.supply(CAROL, "ETH", 25.0);
    a.supply(ALICE, "USDC", 10.0);
    a.borrow(ALICE, "ETH", 0.003);

    let carol_before_a = a.supply_balance(CAROL, "ETH");
    a.set_price("USDC", usd_cents(10));
    a.liquidate(LIQUIDATOR, ALICE, "ETH", 0.001);
    let carol_loss_a = carol_before_a - a.supply_balance(CAROL, "ETH");

    // Scenario B: identical state, but Bob withdraws before the write-down.
    let mut b = setup();
    b.supply(BOB, "ETH", 75.0);
    b.supply(CAROL, "ETH", 25.0);
    b.supply(ALICE, "USDC", 10.0);
    b.borrow(ALICE, "ETH", 0.003);

    let carol_before_b = b.supply_balance(CAROL, "ETH");
    let bob_before_b = b.supply_balance(BOB, "ETH");
    let bob_wallet_before = b.token_balance(BOB, "ETH");

    // The crash is public state. Alice is insolvent from here on, but no
    // write-down has been applied yet.
    b.set_price("USDC", usd_cents(10));
    b.assert_liquidatable(ALICE);

    // Bob exits at the un-written-down index. No gate stops him: the
    // liquidation buffer only guards borrow draws, and `backing_shortfall`
    // still values Alice's uncollateralised debt at face.
    b.withdraw_all(BOB, "ETH");
    let bob_recovered = b.token_balance(BOB, "ETH") - bob_wallet_before;

    b.liquidate(LIQUIDATOR, ALICE, "ETH", 0.001);
    let carol_loss_b = carol_before_b - b.supply_balance(CAROL, "ETH");

    assert!(
        bob_recovered >= bob_before_b,
        "Bob exits whole: supplied={:.9} recovered={:.9}",
        bob_before_b,
        bob_recovered
    );
    assert!(
        carol_loss_b > carol_loss_a,
        "dodging must push loss onto Carol: A={:.9} B={:.9}",
        carol_loss_a,
        carol_loss_b
    );

    // Carol holds 25% of supply, so passing the whole loss to her is ~4x.
    let amplification = carol_loss_b / carol_loss_a;
    assert!(
        amplification > 3.0,
        "expected ~4x concentration onto the remaining supplier, got {:.3}x \
         (A={:.9} B={:.9})",
        amplification,
        carol_loss_a,
        carol_loss_b
    );

    std::println!(
        "A4-econ dodge: bob_supplied={:.9} bob_recovered={:.9} \
         carol_loss_passive={:.9} carol_loss_after_dodge={:.9} amplification={:.3}x",
        bob_before_b,
        bob_recovered,
        carol_loss_a,
        carol_loss_b,
        amplification
    );
}
```

**File:** docs/reference/endpoints.md (L26-30)
```markdown
| `withdraw(caller: Address, account_id: u64, withdrawals: Vec<(HubAssetKey, i128)>, to: Option<Address>) -> Vec<(HubAssetKey, i128)>` | NFT owner/delegate | open | Zero means full withdrawal; returns the amounts paid. |
| `repay(caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>)` | None | open | Anyone can repay; excess returns to caller. |
| `liquidate(liquidator: Address, account_id: u64, debt_payments: Vec<(HubAssetKey, i128)>, seize_mode: SeizeMode) -> u64` | None; credit receiver owner/delegate | open | Pro-rata seizure; Transfer returns 0, Credit returns receiver id. |
| `clean_bad_debt(caller: Address, account_id: u64)` | None | open | Debt exceeds collateral and collateral <= $5; socialize and burn NFT. |
| `flash_loan(caller: Address, asset: HubAssetKey, amount: i128, receiver: Address, data: Bytes)` | None | gated | Wasm callback; pool pulls exact principal plus fee. |
```

**File:** docs/reference/endpoints.md (L59-63)
```markdown
| `paused` | Blocks ordinary entry and exit, including liquidation debt repayment |
| `frozen` | Blocks entry |
| `no_seize` | Blocks collateral seizure |

Seizure checks only `no_seize`. Liquidators cannot choose a different collateral subset. Global pause leaves withdrawal, repayment, liquidation, bad-debt cleanup and recapitalization callable, subject to their other checks.
```
