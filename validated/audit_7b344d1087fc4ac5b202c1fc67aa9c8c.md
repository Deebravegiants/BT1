### Title
Position NFT seller can drain collateral before sale settlement - ([File: contracts/controller/src/positions/supply.rs])

### Summary
A position-NFT owner can advertise or approve the sale of an account containing valuable collateral, then front-run the transfer by withdrawing nearly all collateral or borrowing against it. The buyer receives the same NFT, but the lending account backing it has been stripped of most economic value.

### Finding Description
The controller resolves the current NFT owner for every owner-gated account operation, rather than snapshotting ownership or locking account actions during an NFT approval or pending sale. [1](#0-0) 

`withdraw` requires only current owner or delegate authorization and sends the withdrawn assets to `to`, defaulting to the caller. [2](#0-1) 

Likewise, `borrow` is available to the current owner or delegate and pays the proceeds to `to`, defaulting to the caller, while leaving the debt attached to the account. [3](#0-2) 

The position token exposes the standard OpenZeppelin NFT interface, and transferring it moves control of the whole lending account. [4](#0-3) [5](#0-4) 

Consequently, after granting a marketplace or buyer approval, the seller remains the account owner until settlement and can still execute `withdraw` or `borrow` before `transfer_from` moves the NFT. [6](#0-5) 

### Impact Explanation
A buyer can value the NFT based on its visible supply positions, submit a purchase transaction, and receive an NFT whose backing account has been drained or heavily encumbered by newly minted debt. The seller keeps both the sale proceeds and the withdrawn or borrowed assets, resulting in theft of the buyer's funds.

### Likelihood Explanation
Any unprivileged NFT holder can execute this sequence with `withdraw`, `borrow`, and standard NFT approval/transfer functionality. The attack requires only a secondary sale in which the buyer relies on account state observed before settlement; no privileged role, oracle manipulation, leaked key, or protocol misconfiguration is required.

### Recommendation
Prevent the listed owner from mutating the account while a sale approval is active. Prefer transferring the NFT into a sale escrow before listing, or add an account lock/timelock that disables `withdraw`, `borrow`, and other value-extracting owner operations until the sale completes or is cancelled. Marketplaces should also atomically verify current supply and debt positions during settlement rather than relying on a prior quote.

### Proof of Concept
1. Seller `S` owns position NFT `T`, whose account has `C` collateral and no debt.
2. `S` approves marketplace `M` for token `T`; the approval permits `M` to call `transfer_from` but does not remove `S`'s ownership.
3. Buyer `B` queries `get_account_positions(T)`, observes `C`, and submits a purchase through `M`.
4. `S` front-runs settlement with:
   `withdraw(caller=S, account_id=T, withdrawals=[(hub_asset, C - dust)], to=Some(S))`.
   `process_withdraw` authorizes `S` as the current NFT owner and pays the requested collateral to `S`; leaving `dust` keeps the account and token alive. [7](#0-6) [8](#0-7) 
5. Alternatively, `S` calls `borrow(caller=S, account_id=T, borrows=[...], to=Some(S))` up to the account's borrowing limit, receiving the borrowed assets while the debt remains attached to `T`. [9](#0-8) 
6. `M` executes `transfer_from(spender=M, from=S, to=B, token_id=T)`. `B` pays for the advertised collateralized position but receives a nearly empty collateral account or an account carrying the seller-created debt.

### Citations

**File:** contracts/controller/src/storage/account.rs (L93-104)
```rust
/// Stores a nonempty position map without renewing TTL; deletes an empty map.
fn write_side_map<V: TryFromVal<Env, Val> + IntoVal<Env, Val>>(
    env: &Env,
    key: &ControllerKey,
    map: &Map<HubAssetKey, V>,
) {
    let persistent = env.storage().persistent();
    if map.is_empty() {
        persistent.remove(key);
    } else {
        persistent.set(key, map);
    }
```

**File:** contracts/controller/src/storage/account.rs (L153-160)
```rust
pub(crate) fn try_get_account(env: &Env, account_id: u64) -> Option<Account> {
    let meta = try_get_account_meta(env, account_id)?;
    let owner = try_account_owner(env, account_id)?;
    Some(account_from_parts(
        owner,
        meta,
        get_supply_positions(env, account_id),
        get_debt_positions(env, account_id),
```

**File:** contracts/controller/src/positions/supply.rs (L140-158)
```rust
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
```

**File:** contracts/controller/src/positions/debt.rs (L31-57)
```rust
/// Borrows to `to` or the authorized owner/delegate, then checks solvency.
/// Persists supply alongside debt when the check restamps supply LTVs.
pub(crate) fn process_borrow(
    env: &Env,
    caller: &Address,
    account_id: u64,
    borrows: &Vec<HubPayment>,
    to: Option<Address>,
) {
    validation::require_authorized_caller(env, caller);

    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
    let mut cache = Context::new(env);
    require_external_recipient(env, &mut cache, &recipient);
    let aggregated = payments::aggregate_positive_payments(env, borrows);

    validate_position_entry_gates(
        env,
        &account,
        &aggregated,
        &mut cache,
        AccountPositionType::Borrow,
    );
    settle_borrow(env, &mut account, &recipient, &aggregated, &mut cache);
```

**File:** contracts/position-nft/src/contract.rs (L131-173)
```rust
#[contractimpl(contracttrait)]
impl NonFungibleToken for PositionNft {
    type ContractType = Enumerable;

    /// `{stored base_uri}{token_id}?isStatic=true&chain=STELLAR`
    ///
    /// Panics with the OZ `NonExistentToken` error for burned or never-minted
    /// ids, matching the stock behavior.
    fn token_uri(e: &Env, token_id: u32) -> String {
        let _owner = Base::owner_of(e, token_id);

        let base = Base::base_uri(e);
        let base_len = base.len() as usize;
        // OZ `set_metadata` caps the base at `MAX_BASE_URI_LEN` (200 bytes):
        // 200 + 10 digits (u32 max) + 28-byte suffix fits in 256.
        let mut buf = [0u8; 256];
        base.copy_into_slice(&mut buf[..base_len]);
        let mut len = base_len;
        // Decimal digits, most significant first. token_id >= 1 always
        // (id 0 is consumed at construction), so no zero special-case.
        let mut digits = [0u8; 10];
        let mut n = token_id;
        let mut count = 0usize;
        while n > 0 {
            digits[count] = b'0' + (n % 10) as u8;
            n /= 10;
            count += 1;
        }
        while count > 0 {
            count -= 1;
            buf[len] = digits[count];
            len += 1;
        }
        for b in TOKEN_URI_SUFFIX.bytes() {
            buf[len] = b;
            len += 1;
        }
        String::from_bytes(e, &buf[..len])
    }
}

#[contractimpl(contracttrait)]
impl NonFungibleEnumerable for PositionNft {}
```

**File:** contracts/position-nft/README.md (L39-41)
```markdown
Transferring the token transfers the whole position. Nothing in the controller
changes on transfer: the next controller call resolves the new holder and
accepts it. Collateral and debt both move with the token.
```

**File:** contracts/position-nft/README.md (L168-170)
```markdown
**Approval hands over the whole account.** `approve` and `approve_for_all` let
another address move the position, and moving the position moves the collateral
and the debt with it. See
```
