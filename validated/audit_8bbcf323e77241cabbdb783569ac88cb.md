### Title
Unprivileged `supply` with `account_id = 0` mints unbounded, dust-funded accounts and position-NFT rows with no minimum deposit - (File: contracts/controller/src/positions/supply.rs)

### Summary
`supply` is callable by any address (`require_authorized_caller` only auths the caller's own address) and treats `account_id == 0` as "create a new account owned by the caller". There is no minimum deposit: `aggregate_positive_payments` accepts a 1-unit payment, and `create_account` then mints a position NFT and writes persistent account metadata plus two position maps per call. A single unprivileged address can therefore create an unbounded number of permanent account/NFT storage entries at minimal token cost — the same unbounded-row creation class as the CVE, mapped onto Soroban ledger state instead of a database.

### Finding Description
- `process_supply` calls `load_or_create_account`, which for `account_id == 0` immediately calls `create_account` and mints an NFT via `nft_mint_call` before any amount check beyond positivity [1](#0-0) [2](#0-1) .
- Each minted account writes `AccountMeta`, an `Account` with empty `supply_positions`/`borrow_positions` maps, and a full NFT (owner, balance, enumeration) entry set, with no cap on total accounts [3](#0-2) .
- The only amount gate is `AmountMustBePositive` on the measured transfer; a 1-unit deposit of any listed asset suffices [4](#0-3) .
- `POSITION_LIMIT_MAX` bounds positions *within* an account, not the number of accounts, so it does not mitigate this [5](#0-4) .
- The repo's own PoC test `poc_single_actor_spams_unbounded_dust_accounts` demonstrates 64 distinct persistent accounts created by one actor with 1-unit deposits [6](#0-5) .
- The same path is reachable through `flash_position`, `multiply`, and `migrate_from_blend` with `account_id = 0`, all permissionless for a new caller-owned account [7](#0-6) .

### Impact Explanation
Each call permanently grows contract and NFT-contract ledger state: account metadata, two position maps, NFT ownership/balance/enumeration entries. Unlike the deposit tokens, which are tiny, the state footprint per account is large and is never garbage-collected — `renew_account` is owner-gated, but archived persistent entries remain restorable state forever and the NFT enumeration grows monotonically. This is unbounded resource allocation by an unauthenticated-in-effect caller: the attacker funds N accounts with N stroops-equivalent dust and forces the protocol's state tree to absorb the full per-account entry set, inflating rent/restore surface and archival burden for every subsequent operation that touches account or NFT storage.

### Likelihood Explanation
No governance action, privilege, or market precondition is needed beyond one listed asset — which exists in any live deployment. The attacker's cost is one positive token unit plus transaction fees per account, and the whole loop is a simple repeated `supply(attacker, 0, spoke, [(asset, 1)])`. The shipped PoC test confirms the loop succeeds verbatim today.

### Recommendation
Enforce a minimum initial deposit denominated in USD terms (e.g., reuse `min_borrow_collateral_usd` semantics or a dedicated `min_account_collateral_usd`) on the `account_id == 0` path in `create_account`/`process_supply`, evaluated post-measurement, so dust cannot seed an account. Alternatively require a refundable account-creation bond. At minimum, reject `account_id == 0` supplies whose aggregate value is below a dust floor.

### Proof of Concept
See `tests/test-harness/tests/controller/supply.rs:312-344` (`poc_single_actor_spams_unbounded_dust_accounts`): mint `N` units of USDC to one attacker, loop `ctrl.supply(&attacker, &0u64, &1u32, &[(asset, 1i128)])`, and assert each call returns a fresh `account_id` that persists via `account_exists`. Extending `N` arbitrarily demonstrates the unbounded growth.

### Citations

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

**File:** contracts/controller/src/positions/supply.rs (L116-129)
```rust
    for (hub_asset, amount_in) in aggregated.iter() {
        let asset_config: AssetConfig = cache.require_spoke_asset(account.spoke_id, &hub_asset);
        let received = payments::transfer_amount_measured(
            env,
            &hub_asset.asset,
            caller,
            &pool_addr,
            amount_in,
            GenericError::AmountMustBePositive,
        );
        let position = account.get_or_create_supply_position(&hub_asset, &asset_config);
        entries.push_back(PoolSupplyEntry {
            action: make_pool_action(&position, received, hub_asset.clone()),
        });
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

**File:** tests/test-harness/tests/controller/supply.rs (L312-344)
```rust
#[test]
fn poc_single_actor_spams_unbounded_dust_accounts() {
    let mut t = LendingTest::new().with_market(usdc_preset()).build();

    let attacker = t.get_or_create_user("attacker");
    let usdc = t.resolve_market("USDC");

    const N: u64 = 64;
    usdc.token_admin.mint(&attacker, &(N as i128));
    let asset = usdc.asset.clone();

    let ctrl = t.ctrl_client();
    let mut created: u64 = 0;
    let mut last_id: u64 = 0;
    for _ in 0..N {
        let dust = vec![&t.env, (hub_asset(asset.clone()), 1i128)];
        let id = ctrl.supply(&attacker, &0u64, &1u32, &dust);
        assert!(id > 0, "1-unit deposit must be accepted (no dust floor)");

        assert!(id > last_id, "each supply(id=0) must mint a new account id");
        assert!(
            ctrl.account_exists(&id),
            "spammed account persists in storage"
        );
        last_id = id;
        created += 1;
    }

    assert_eq!(
        created, N,
        "one actor created {N} distinct accounts with dust deposits"
    );
}
```

**File:** contracts/controller/README.md (L73-90)
```markdown
| `supply` | `fn supply( env: Env, caller: Address, account_id: u64, spoke_id: u32, assets: Vec<(HubAssetKey, i128)>, ) -> u64` | blocked by global pause | Supplies `assets` as collateral to `account_id` in spoke `spoke_id`, creating a new account when `account_id` is 0, and returns the account id. |
| `borrow` | `fn borrow( env: Env, caller: Address, account_id: u64, borrows: Vec<(HubAssetKey, i128)>, to: Option<Address>, )` | blocked by global pause | Borrows `borrows` against `account_id`'s collateral, sending the funds to `to` if provided or to the caller otherwise; reverts if the resulting position breaches the account's solvency limits. |
| `withdraw` | `fn withdraw( env: Env, caller: Address, account_id: u64, withdrawals: Vec<(HubAssetKey, i128)>, to: Option<Address>, ) -> Vec<(HubAssetKey, i128)>` | — | Withdraws `withdrawals` from `account_id`'s supplied collateral, sending the funds to `to` if provided or to the caller otherwise, and returns the amounts actually withdrawn; a zero amount for an asset withdraws the entire position. |
| `repay` | `fn repay(env: Env, caller: Address, account_id: u64, payments: Vec<(HubAssetKey, i128)>)` | — | Repays `payments` against `account_id`'s debt positions, pulling the funds from the caller and refunding any excess. |
| `liquidate` | `fn liquidate( env: Env, liquidator: Address, account_id: u64, debt_payments: Vec<(HubAssetKey, i128)>, seize_mode: SeizeMode, ) -> u64` | — | Liquidates `account_id` by having `liquidator` repay `debt_payments` and seizing collateral at a bonus scaled by the account's health factor. Returns the `Credit` receiver's account id, or 0 for `Transfer`. |
| `clean_bad_debt` | `fn clean_bad_debt(env: Env, caller: Address, account_id: u64)` | — | Socializes `account_id`'s debt into the supply index and removes the account when it is insolvent and its remaining collateral value is at or below the dust threshold; reverts otherwise. |

### Strategies and flash loans

| Entrypoint | Signature | Notes | What it does |
| --- | --- | --- | --- |
| `flash_loan` | `fn flash_loan( env: Env, caller: Address, asset: HubAssetKey, amount: i128, receiver: Address, data: Bytes, )` | blocked by global pause | Flash-loans `amount` of `asset` to `receiver`, invoking its callback with `data`; the pool pulls back the principal plus fee before the call returns. |
| `flash_position` | `fn flash_position( env: Env, caller: Address, account_id: u64, spoke_id: u32, mode: PositionMode, debt: HubAssetKey, amount: i128, receiver: Address, data: Bytes, collaterals: Vec<(HubAssetKey, i128)>, refund_assets: Vec<Address>, ) -> u64` | blocked by global pause | Mints `amount` of `debt` onto `account_id` with no flash fee, forwards the measured tokens to `receiver`, invokes `execute_flash_position`, and deposits measured controller-balance increases of `collaterals`; the account must be solvent after the callback. Returns the account id; `account_id` 0 creates a new account. |
| `multiply` | `fn multiply( env: Env, caller: Address, account_id: u64, spoke_id: u32, collateral: HubAssetKey, debt_to_flash_loan: i128, debt: HubAssetKey, mode: PositionMode, swap: Bytes, initial_payment: Option<(HubAssetKey, i128)>, convert_swap: Option<Bytes>, ) -> u64` | blocked by global pause | Opens or extends a leveraged position on `account_id`: borrows `debt_to_flash_loan` of `debt`, swaps it into `collateral` via `swap`, and deposits the result. An `initial_payment` in `collateral` joins the deposit, one in `debt` joins the swap, and one in a third asset needs `convert_swap`. Returns the account id; `account_id` 0 creates a new account. |
| `swap_debt` | `fn swap_debt( env: Env, caller: Address, account_id: u64, existing_debt: HubAssetKey, amount: i128, new_debt: HubAssetKey, swap: Bytes, )` | blocked by global pause | Replaces `account_id`'s `existing_debt` position with `new_debt` by borrowing `amount` of `new_debt`, swapping it to `existing_debt` via `swap`, and repaying the existing position with the proceeds. |
| `swap_collateral` | `fn swap_collateral( env: Env, caller: Address, account_id: u64, current: HubAssetKey, amount: i128, new: HubAssetKey, swap: Bytes, )` | blocked by global pause | Replaces `amount` of `account_id`'s `current` collateral with `new` by withdrawing it, swapping to `new` via `swap`, and depositing the proceeds as collateral. |
| `repay_debt_with_collateral` | `fn repay_debt_with_collateral( env: Env, caller: Address, account_id: u64, collateral: HubAssetKey, collateral_amount: i128, debt: HubAssetKey, swap: Bytes, close_position: bool, )` | blocked by global pause | Repays `account_id`'s `debt` position using `collateral_amount` of `collateral`, netting them directly when the two assets match or swapping via `swap` otherwise. |
| `migrate_from_blend` | `fn migrate_from_blend( env: Env, caller: Address, account_id: u64, spoke_id: u32, hub_id: u32, blend_pool: Address, collateral_assets: Vec<Address>, supply_assets: Vec<Address>, debt_caps: Vec<(Address, i128)>, ) -> u64` | blocked by global pause | Migrates the caller's position from `blend_pool` (which must be approved) into `account_id`: borrows each `debt_caps` amount, repays the caller's Blend debt, repays the unused borrow, then sweeps `collateral_assets` and `supply_assets` from Blend into the pool as collateral. Returns the account id; `account_id` 0 creates a new account. |
```
