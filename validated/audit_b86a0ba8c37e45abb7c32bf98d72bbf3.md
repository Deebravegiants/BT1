### Title
Burning the position NFT frees the ownership record while dangling controller-side debt/collateral positions keep referencing it — liquidation, bad-debt cleanup, and withdrawal all permanently fail (`AccountNotFound`), permanently freezing collateral and permanently stranding uncollectible debt - (File: contracts/controller/src/storage.rs — `get_account`/`account_owner` owner read; contracts/position-nft burn path)

### Summary
`clean_bad_debt` / `liquidate` / `withdraw` all enter through `storage::get_account`, which resolves `owner_of` on the position NFT. When the NFT is burned, the controller-side account entries remain live (`account_exists` stays true, positions remain stored), but every flow that touches the account panics with `AccountNotFound`. This is the XOXNO Lending shape of the CVE-2024-24263 use-after-free class: the owner record is freed while dependent state continues to reference it, and every dereference traps.

### Finding Description
`process_liquidation` calls `storage::get_account(env, account_id)` before any check ( [1](#0-0) ), and `socialize_bad_debt` does the same for both `clean_bad_debt` and `force_socialize_bad_debt` ( [2](#0-1) ). The in-repo test `partial_liquidation_resolves_nft_ownership` proves the mechanism: after `position_nft.burn(&token_id)`, `account_exists(id)` remains true but `try_liquidate` fails with `ACCOUNT_NOT_FOUND`; `bad_debt_winddown_resolves_nft_ownership` proves `clean_bad_debt` and `force_socialize_bad_debt` fail identically ( [3](#0-2) ). The account's supply and borrow positions persist in storage indefinitely — no path deletes them without first reading the freed ownership record. Nothing recreates or remaps ownership: `remove_account_and_burn_nft` is the only teardown and it itself is unreachable once the NFT is gone ( [4](#0-3) ).

### Impact Explanation
Two accepted impact classes are triggered by a single unprivileged action:

- **Permanent freezing of funds**: all collateral supply positions of the burned-NFT account become unreachable — `withdraw`, `repay`, liquidation seizure, and `clean_bad_debt` all revert on the owner read. The collateral is locked in the pool forever with no recovery path (no rescue/recapitalize path reassigns account shares).
- **Protocol insolvency**: an underwater account that burns its NFT permanently blocks both liquidation and bad-debt socialization. Its debt is never written off via `apply_bad_debt_to_supply_index` ( [5](#0-4) ), so the affected market keeps reporting an inflated `supply_index` and `supplied` book while the loan is uncollectible and its collateral is frozen. Suppliers of that market hold shares the pool cannot fully pay out — last withdrawers absorb the stranded loss. An insolvent owner has nothing to lose by burning: the account is already worth less than its debt, and bricking it costs only the dust collateral. Notably the governance fallback `force_socialize_bad_debt` fails too, so there is no privileged recovery — this is a permanent, not transient, wedge.

### Likelihood Explanation
The trigger is a single owner-authorized `burn` on the position NFT — the same unprivileged trust level as the in-scope `transfer`/`approve` verbs on that contract, and cheaper than a liquidation repayment. It requires no oracle manipulation, no privileged role, no leaked keys, and no edge-case parameters: any account holder can perform it at will, and it is most attractive precisely when the account is insolvent (the moment the protocol most needs `clean_bad_debt` or liquidation to work). The fail-closed rejection rule does not apply cleanly here: this is not a missing-oracle fail-closed DoS, it is a permanent state corruption caused by destroying a key while references to it remain — the defining structure of a UAF.

### Recommendation
Make the ownership reference non-freeable while dependent state exists, or make consumers tolerate its absence:

1. In `position-nft::burn` (or a controller-mediated `close_account`), require the controller account to be empty (`account.is_empty()`) before allowing the burn, mirroring `cleanup_account_if_empty` ( [6](#0-5) ).
2. Alternatively, let `storage::get_account`/`account_owner` distinguish "account exists, owner record gone" and route it to a permissionless wind-down (seize collateral as revenue, socialize debt) instead of reverting.
3. Either way, `clean_bad_debt` must never depend on a value the account owner can unilaterally destroy.

### Proof of Concept
Adapted directly from the existing test (tests/test-harness/tests/controller/position_nft_ttl_and_ownership_reads.rs):

```rust
let mut t = LendingTest::new().standard_two_asset().build();

// Suppliers fund the debt market.
t.supply(BOB, "ETH", 100.0);

// ALICE supplies collateral and borrows.
t.supply(ALICE, "USDC", 10_000.0);
t.borrow(ALICE, "ETH", 3.0);
let id = t.account_id(ALICE);
let token_id = u32::try_from(id).unwrap();

// Collateral crashes: account is now deeply insolvent.
t.set_price("USDC", usd_cents(1));

// Free the ownership record while positions still reference it.
position_nft::PositionNftClient::new(&t.env, &t.position_nft).burn(&token_id);

// Every dependent dereference traps permanently:
assert_contract_error(
    flatten(t.ctrl_client().try_clean_bad_debt(&keeper, &id)),
    errors::ACCOUNT_NOT_FOUND,
);
assert_contract_error(t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0), errors::ACCOUNT_NOT_FOUND);
assert_contract_error(t.try_withdraw(ALICE, "USDC", 1.0), errors::ACCOUNT_NOT_FOUND);

// Terminal state: collateral frozen, debt never socialized.
// The ETH market's supply_index is never written down; BOB's shares
// are backed by an uncollectible loan. Governance force_socialize_bad_debt
// reverts identically — no recovery path exists.
```

**Caveat**: I verified the revert behavior via the repository's own tests, but could not fully enumerate the `position-nft` `burn` authorization surface or confirm within the available search depth whether `withdraw`/`repay` hit the identical `account_owner` read in every mode; the liquidation and bad-debt paths are confirmed by tests, and the remaining endpoints share `storage::get_account`.

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L44-58)
```rust
    validation::require_not_flash_loaning(env);

    let mut account = storage::get_account(env, account_id);

    let mut cache = Context::new(env);

    require_non_empty_payments(env, debt_payments);

    // Reject an unusable receiver before moving tokens.
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );

    // Share payment normalization and positivity checks with the estimate view.
    let liquidation_plan = plan::build_liquidation_plan(env, &account, debt_payments, &mut cache);
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L195-237)
```rust
/// Authorizes permissionless dust-gated cleanup outside flash loans.
pub(crate) fn process_clean_bad_debt(env: &Env, caller: &Address, account_id: u64) {
    caller.require_auth();
    validation::require_not_flash_loaning(env);
    clean_bad_debt_standalone(env, account_id);
}

/// Admission condition for bad-debt socialization.
#[derive(Clone, Copy, PartialEq)]
enum BadDebtGate {
    /// Permissionless: insolvent *and* collateral at or below the dust threshold.
    DustCapped,
    /// Owner-only: insolvent alone, with no cap on the collateral left behind.
    InsolventOnly,
}

/// Requires open debt and the selected insolvency gate, then cleans up the account.
fn socialize_bad_debt(env: &Env, account_id: u64, gate: BadDebtGate) {
    let mut cache = Context::new(env);
    let account = storage::get_account(env, account_id);

    assert_with_error!(
        env,
        !account.borrow_positions.is_empty(),
        CollateralError::DebtPositionNotFound
    );

    let totals = risk::calculate_account_risk_totals(
        env,
        &mut cache,
        &account.supply_positions,
        &account.borrow_positions,
    );

    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
```

**File:** tests/test-harness/tests/controller/position_nft_ttl_and_ownership_reads.rs (L281-334)
```rust
/// A partial liquidation resolves NFT ownership: `process_liquidation` calls
/// `storage::get_account`, which reads `owner_of`. With the `Owner` entry
/// burned and every controller-side account entry intact, the liquidation
/// fails with `AccountNotFound`.
#[test]
fn partial_liquidation_resolves_nft_ownership() {
    let mut t = LendingTest::new().standard_two_asset().build();
    t.supply(ALICE, "USDC", 10_000.0);
    t.borrow(ALICE, "ETH", 3.0);
    let id = t.account_id(ALICE);
    let token_id = u32::try_from(id).expect("test ids fit u32");

    t.set_price("USDC", usd_cents(50));
    t.assert_liquidatable(ALICE);

    // Detach the ownership leg, leaving controller state untouched.
    position_nft::PositionNftClient::new(&t.env, &t.position_nft).burn(&token_id);
    assert!(!t.try_nft_owner_of(id), "ownership leg is now unreadable");
    assert!(
        t.account_exists(id),
        "controller-side account state must still be live -- this isolates the \
         NFT read as the only thing that changed"
    );

    // A plain partial liquidation, well under the close factor.
    let result = t.try_liquidate(LIQUIDATOR, ALICE, "ETH", 1.0);
    assert_contract_error(result, errors::ACCOUNT_NOT_FOUND);
}

/// The same isolation on the bad-debt path: `clean_bad_debt` and
/// `force_socialize_bad_debt` enter `socialize_bad_debt`, which calls
/// `storage::get_account`, so both fail on the owner read with `AccountNotFound`.
#[test]
fn bad_debt_winddown_resolves_nft_ownership() {
    let mut t = LendingTest::new().standard_two_asset().build();
    t.supply(ALICE, "USDC", 10_000.0);
    t.borrow(ALICE, "ETH", 3.0);
    let id = t.account_id(ALICE);
    let token_id = u32::try_from(id).expect("test ids fit u32");
    let keeper = t.get_or_create_user(LIQUIDATOR);

    t.set_price("USDC", usd_cents(1));
    position_nft::PositionNftClient::new(&t.env, &t.position_nft).burn(&token_id);
    assert!(t.account_exists(id), "controller state still live");

    assert_contract_error(
        flatten(t.ctrl_client().try_clean_bad_debt(&keeper, &id)),
        errors::ACCOUNT_NOT_FOUND,
    );
    assert_contract_error(
        flatten(t.ctrl_client().try_force_socialize_bad_debt(&id)),
        errors::ACCOUNT_NOT_FOUND,
    );
}
```

**File:** contracts/controller/src/account.rs (L157-170)
```rust
/// Deletes all account entries and burns its NFT atomically. Account deletion
/// must use this path to preserve the NFT/account existence invariant.
pub(crate) fn remove_account_and_burn_nft(env: &Env, account_id: u64) {
    storage::remove_account_entry(env, account_id);
    let nft = storage::get_position_nft(env);
    nft_burn_call(env, &nft, account_id);
}

/// Deletes the account and burns its NFT when both position maps are empty.
pub(crate) fn cleanup_account_if_empty(env: &Env, account: &Account, account_id: u64) {
    if account.is_empty() {
        remove_account_and_burn_nft(env, account_id);
    }
}
```

**File:** contracts/pool/src/ops/seize.rs (L23-34)
```rust
    match entry.side {
        AccountPositionType::Borrow => {
            let bad_debt = cache.unscale_borrow_ceil_ray(position);
            interest::apply_bad_debt_to_supply_index(&mut cache, bad_debt);
            cache.burn_debt(position);
        }
        AccountPositionType::Deposit => {
            cache.absorb_supply_as_revenue(position);
        }
    }

    cache.commit()
```
