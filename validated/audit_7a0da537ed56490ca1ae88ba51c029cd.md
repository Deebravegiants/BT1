### Title
Unbounded dust account creation can exhaust the `u32` position NFT namespace and permanently disable new accounts - (File: contracts/position-nft/src/contract.rs)

### Summary
`Controller::supply` lets any authorized caller pass `account_id = 0` to create a new account, with only a strictly positive asset amount required. [1](#0-0)  Each account creation calls `PositionNft::mint`, which allocates a sequential `u32` token id. [2](#0-1) [3](#0-2)  Token id `0` is reserved as the account-creation sentinel, and burned ids are never reused, leaving approximately `2^32 - 1` usable account ids. [4](#0-3) [5](#0-4) 

### Finding Description
`supply` authenticates `caller`, accepts any nonempty list of positive amounts, and invokes `load_or_create_account`; when `account_id == 0`, that helper creates an account owned by the caller. [6](#0-5) [7](#0-6)  The helper unconditionally calls `nft_mint_call`, which invokes `PositionNftClient::mint` and widens the returned `u32` token id to a `u64` account id. [8](#0-7) [9](#0-8) 

There is no account-creation fee or minimum economic deposit: `1` raw unit of a listed collateral asset is sufficient. [10](#0-9)  The depositor can withdraw the full position by passing amount `0`; normal withdrawal assigns `protocol_fee: 0`, and emptying both position maps burns the NFT without making its id available again. [11](#0-10) [12](#0-11) [13](#0-12) 

After the sequential `u32` namespace is consumed, `Enumerable::sequential_mint` cannot return another in-domain token id, so every subsequent account-creation call aborts. [14](#0-13) 

### Impact Explanation
An attacker can permanently prevent creation of new lending accounts without stealing existing pool funds. [15](#0-14)  The most direct victim is `supply(caller, 0, spoke_id, assets)`, which can no longer open a Normal account once minting fails. [16](#0-15)  Other user-facing flows that create an account through `account_id = 0`, including `multiply`, `flash_position`, `migrate_from_blend`, and liquidation credit receivers, depend on the same finite NFT id allocation and become unavailable for new positions. [17](#0-16) 

Existing accounts retain their withdrawal, repayment, liquidation, and maintenance paths, but all future position creation remains permanently disabled unless the NFT/controller architecture is migrated or upgraded. [18](#0-17) 

### Likelihood Explanation
The attack requires one valid, active, collateralizable market and enough authorization fees and storage rent to submit roughly `2^32` account-creation operations. [19](#0-18)  The protocol itself charges no mint fee, requires only a one-unit positive deposit, and allows that deposit to be withdrawn and reused after each burn. [7](#0-6) [12](#0-11) 

The attack is therefore bounded by aggregate transaction cost rather than by a protocol-level account cap, fee, deposit burn, per-owner limit, or reusable-id mechanism. [5](#0-4)  This is a Medium-severity permanent availability failure: execution requires a sustained high-volume attack, but successful exhaustion permanently disables the protocol's position-onboarding function. [15](#0-14) 

### Recommendation
Move account/token ids to a substantially wider type such as `u128` and update `PositionNft::mint`, `nft_mint_call`, account storage keys, views, and integrations consistently. [18](#0-17)  If `u32` ids must remain, charge a non-refundable native-token fee or enforce a non-returnable account-creation reserve large enough to make namespace exhaustion economically irrational. [2](#0-1) 

Do not rely on a per-address limit because the attacker can generate additional addresses; any mitigation must bound or price the global monotonic counter. [20](#0-19) 

### Proof of Concept
1. Select an active listed collateral asset and construct `key = HubAssetKey { hub_id: valid_hub, asset }`.
2. Call `supply(attacker, 0, active_spoke_id, vec![(key, 1)])`; the call authenticates the attacker, accepts the one-unit payment, creates a new account, mints a fresh sequential NFT id, and returns that id. [1](#0-0) [2](#0-1) 
3. Call `withdraw(attacker, returned_id, vec![(key, 0)], None)`; the zero amount requests the full position, pays it without a protocol withdrawal fee, removes the account, and burns the NFT. [21](#0-20) [13](#0-12) 
4. Repeat the two calls with the recovered unit or with new dust deposits; every iteration consumes one new sequential `u32` id and no burned id becomes reusable. [22](#0-21) [5](#0-4) 
5. Once the namespace is exhausted, call `supply(attacker, 0, active_spoke_id, vec![(key, 1)])` again; execution reaches `nft_mint_call`, but `Enumerable::sequential_mint` cannot produce another valid `u32` id and the transaction reverts. [9](#0-8) [14](#0-13)

### Citations

**File:** contracts/controller/src/positions/supply.rs (L40-63)
```rust
pub(crate) fn process_supply(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    assets: &Vec<HubPayment>,
) -> u64 {
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);

    process_deposit(env, caller, &mut account, &aggregated, &mut cache);
```

**File:** contracts/controller/src/positions/supply.rs (L138-168)
```rust
/// Withdraws for an authorized owner/delegate and checks post-pool solvency.
/// Zero requests withdraw all; returns the pool's actual payouts per asset.
pub(crate) fn process_withdraw(
    env: &Env,
    caller: &Address,
    account_id: u64,
    withdrawals: &Vec<HubPayment>,
    to: Option<Address>,
) -> Vec<HubPayment> {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_payments(env, withdrawals, payments::ZeroLeg::MeansAll);

    let paid = settle_withdraw(env, &mut account, &recipient, &aggregated, &mut cache);
    let _ = enforce_post_pool_solvency(env, &mut cache, &mut account);

    finalize_position_flow(
        env,
        account_id,
        &account,
        &mut cache,
        PositionSides::Supply,
        true,
    );
    paid
```

**File:** contracts/controller/src/positions/supply.rs (L189-198)
```rust
        let position = get_supply_position_or_panic(env, account, &hub_asset);
        let requested = if amount == 0 {
            WITHDRAW_ALL_SENTINEL
        } else {
            amount
        };
        entries.push_back(PoolWithdrawEntry {
            action: make_pool_action(&position, requested, hub_asset.clone()),
            protocol_fee: 0,
        });
```

**File:** contracts/controller/src/account.rs (L24-39)
```rust
/// Mints an account NFT and stores empty-account metadata in an active spoke.
pub(crate) fn create_account(
    env: &Env,
    owner: &Address,
    spoke_id: u32,
    mode: PositionMode,
    cache: &mut Context,
) -> (u64, Account) {
    create_account_with(
        env,
        owner,
        spoke_id,
        mode,
        cache,
        SpokeAdmission::ActiveOnly,
    )
```

**File:** contracts/controller/src/account.rs (L62-73)
```rust
    let nft = storage::get_position_nft(env);
    let account_id = nft_mint_call(env, &nft, owner);
    let account = Account {
        owner: owner.clone(),
        spoke_id,
        mode,
        supply_positions: Map::new(env),
        borrow_positions: Map::new(env),
    };
    storage::set_account_meta(env, account_id, &AccountMeta { spoke_id, mode });

    (account_id, account)
```

**File:** contracts/controller/src/account.rs (L86-97)
```rust
pub(crate) fn load_or_create_account(
    env: &Env,
    caller: &Address,
    account_id: u64,
    spoke_id: u32,
    mode: PositionMode,
    guard: AccountGuard,
    cache: &mut Context,
) -> (u64, Account) {
    if account_id == 0 {
        return create_account(env, caller, spoke_id, mode, cache);
    }
```

**File:** contracts/controller/src/account.rs (L157-169)
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
```

**File:** contracts/position-nft/src/contract.rs (L53-75)
```rust
    /// `controller` is the only address allowed to mint, burn and upgrade. Consumes
    /// token id 0 so the first position is id 1 — the controller ABI reserves
    /// account id 0 as the "create new account" sentinel.
    pub fn __constructor(e: &Env, controller: Address, uri: String, name: String, symbol: String) {
        e.storage()
            .instance()
            .set(&DataKey::Controller, &controller);
        Base::set_metadata(e, uri, name, symbol);
        sequential::increment_token_id(e, 1);
    }

    /// Mints the next sequential position token to `to`. Controller-only.
    ///
    /// Renews the instance TTL (controller address, collection metadata and
    /// id counter) on every account creation (INV-STOR-02a).
    pub fn mint(e: &Env, to: Address) -> u32 {
        controller(e).require_auth();
        renew_instance(e);
        let token_id = Enumerable::sequential_mint(e, &to);
        // sequential_mint writes Owner/Balance at the network minimum TTL; lift
        // them to the user window so a new position does not archive early.
        extend_user_persistent_ttl(e, &to, token_id);
        token_id
```

**File:** contracts/position-nft/src/contract.rs (L88-95)
```rust
    pub fn burn(e: &Env, token_id: u32) {
        controller(e).require_auth();
        renew_instance(e);
        let owner = Base::owner_of(e, token_id);
        Base::update(e, Some(&owner), None, token_id);
        emit_burn(e, &owner, token_id);
        Enumerable::remove_from_enumerations(e, &owner, token_id);
    }
```

**File:** contracts/position-nft/README.md (L151-154)
```markdown

**Token ids are never reused.** Ids come from `increment_token_id`, a
monotonic instance counter. `burn` does not decrement it. A burned id can never
be minted again, so a deleted account id cannot be resurrected.
```

**File:** contracts/controller/src/payments.rs (L64-80)
```rust
/// Aggregates hub-asset payments, requiring every amount to be positive.
pub(crate) fn aggregate_positive_payments(
    env: &Env,
    payments: &Vec<HubPayment>,
) -> Vec<HubPayment> {
    aggregate_payments(env, payments, ZeroLeg::Rejected)
}

/// Aggregates hub-asset payments in first-seen order. Rejects empty input,
/// negative amounts, and overflow. Under `MeansAll`, any zero leg sets that
/// hub asset's total to zero (withdraw all), whatever the other legs hold.
pub(crate) fn aggregate_payments(
    env: &Env,
    payments: &Vec<HubPayment>,
    zero_leg: ZeroLeg,
) -> Vec<HubPayment> {
    require_non_empty_payments(env, payments);
```

**File:** contracts/controller/src/payments.rs (L103-122)
```rust
/// Adds one amount to a hub asset's total under the selected zero policy.
fn aggregate_payment_amount(
    env: &Env,
    previous: Option<i128>,
    amount: i128,
    zero_leg: ZeroLeg,
) -> i128 {
    // Validate before the zero sentinel can mask a negative amount.
    require_nonneg_amount(env, amount);

    match (zero_leg, amount, previous) {
        (ZeroLeg::Rejected, 0, _) => {
            panic_with_error!(env, GenericError::AmountMustBePositive);
        }
        (ZeroLeg::MeansAll, 0, _) | (ZeroLeg::MeansAll, _, Some(0)) => 0,
        (_, amount, previous) => previous
            .unwrap_or(0)
            .checked_add(amount)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
    }
```

**File:** contracts/controller/src/external/position_nft.rs (L5-24)
```rust
/// Mints a position NFT and widens its sequential `u32` ID to a `u64` account ID.
pub(crate) fn nft_mint_call(env: &Env, nft: &Address, to: &Address) -> u64 {
    u64::from(PositionNftClient::new(env, nft).mint(to))
}

/// Burns the NFT; IDs outside the mintable `u32` domain fail with `AccountNotFound`.
pub(crate) fn nft_burn_call(env: &Env, nft: &Address, account_id: u64) {
    let token_id = u32::try_from(account_id)
        .unwrap_or_else(|_| panic_with_error!(env, GenericError::AccountNotFound));
    PositionNftClient::new(env, nft).burn(&token_id);
}

/// Returns current NFT ownership. Out-of-range IDs, missing tokens, and failed
/// lookups return `None`, so ownership checks fail closed.
pub(crate) fn nft_try_owner_of_call(env: &Env, nft: &Address, account_id: u64) -> Option<Address> {
    let token_id = u32::try_from(account_id).ok()?;
    match PositionNftClient::new(env, nft).try_owner_of(&token_id) {
        Ok(Ok(owner)) => Some(owner),
        _ => None,
    }
```

**File:** contracts/controller/src/lib.rs (L90-102)
```rust
    /// Supplies `assets` as collateral and returns the account id; `account_id = 0`
    /// creates an account in `spoke_id`. Third parties may only top up existing
    /// supply positions; owners and delegates may add assets.
    #[when_not_paused]
    fn supply(
        env: Env,
        caller: Address,
        account_id: u64,
        spoke_id: u32,
        assets: Vec<(HubAssetKey, i128)>,
    ) -> u64 {
        positions::process_supply(&env, &caller, account_id, spoke_id, &assets)
    }
```

**File:** docs/reference/endpoints.md (L45-49)
```markdown
### Accounts and authorization

Account id `0` creates an account on `supply`, `multiply`, `flash_position`, `migrate_from_blend`, and liquidation with `Credit(0)`. An account's spoke binding is permanent. `multiply` and `flash_position` require Multiply, Long or Short mode, and an existing account must match the requested mode. Blend migration creates a Normal account; an existing destination need not be Normal.

Delegates belong to the granting owner. An NFT transfer disables that owner's grants; a transfer back can reactivate them unless a later owner has replaced or deleted the list. NFT ownership, including control of collateral and the debt obligation, transfers atomically.
```

**File:** contracts/controller/src/positions/mod.rs (L230-252)
```rust
/// Checks position-count limits and entry permissions for all aggregated assets.
pub(crate) fn validate_position_entry_gates(
    env: &Env,
    account: &Account,
    aggregated: &AggregatedPayments,
    cache: &mut Context,
    position_type: AccountPositionType,
) {
    validation::validate_bulk_position_limits(env, account, position_type, aggregated);
    if matches!(position_type, AccountPositionType::Deposit) {
        validation::require_whole_unit_isolation(env, cache, account, aggregated);
    }

    for (hub_asset, _) in aggregated {
        match position_type {
            AccountPositionType::Deposit => {
                require_can_supply(env, cache, account.spoke_id, &hub_asset);
            }
            AccountPositionType::Borrow => {
                require_can_borrow(env, cache, account.spoke_id, &hub_asset);
            }
        }
    }
```
