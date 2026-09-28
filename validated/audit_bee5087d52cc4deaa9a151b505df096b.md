### Title
Spending authority is checked against the creation-time `Account.owner`, not the live position-NFT owner, so a transferred account remains controllable by the previous holder - ([File: contracts/controller/src/account.rs])

### Summary
Account spending authority (`require_owner_or_delegate`) trusts the `owner` field stored inside the `Account` struct at creation time, while other paths (`require_account_owner`, `renew_account`, `add_delegate`) correctly resolve the current owner from the position NFT. Because `position-nft::transfer` moves the NFT (and the permissionless inventory only states that the previous owner's delegate grants go inactive), the stored `Account.owner` can remain the previous holder, leaving them — a now-unprivileged address — with full owner-equivalent authority over an account they no longer own. This is the direct analog of CVE-2023-32316's missing permission check: authority is derived from a stale, self-referential field instead of the authoritative identity source.

### Finding Description
- `create_account` persists `owner` into the `Account` struct once, at mint time (`account.rs` lines 62–70). [1](#0-0) 
- `is_owner_or_delegate` returns `true` when `caller == owner`, where `owner` is `account.owner` loaded from `storage::get_account`, with no NFT ownership re-resolution [2](#0-1) 
- `require_owner_or_delegate` gates every fund-moving path on this check: `process_withdraw` [3](#0-2) , `borrow`, `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend`, and the `Migrate`/`Multiply` guards in `load_or_create_account` [4](#0-3) 
- By contrast, `require_account_owner` resolves the *live* NFT owner via `storage::account_owner` [5](#0-4) , confirming the NFT is the authoritative ownership source — and that the spend path uses a different, weaker source.
- `position-nft::transfer` is a stock OpenZeppelin NFT move; the declared exception notes only that "delegate grants from the previous owner go inactive" — nothing rewrites `Account.owner` in the controller, and the NFT contract cannot touch controller storage. [6](#0-5) 

Attack path (single unprivileged address, allowed entrypoints only): Alice creates an account, supplies collateral, then calls `position-nft::transfer` to sell/gift the account to Bob. `Account.owner` still reads Alice. Alice calls `controller::borrow(account_id, …)` or `withdraw(account_id, …)` as the stale owner — `require_owner_or_delegate` passes — draining collateral backed by a position Bob believes he owns. Bob himself is also unable to act, since `caller == account.owner` fails for him.

### Impact Explanation
Theft of user funds: the prior NFT holder retains borrow/withdraw authority and can extract the account's collateral value up to solvency limits, or withdraw outright if unleveraged. Secondary effect: the legitimate new owner is locked out of all owner-gated flows (`withdraw`, `borrow`, strategies), causing freezing of funds even absent malice.

### Likelihood Explanation
Any account NFT transfer creates the condition; no governance action, oracle manipulation, or timing is required. The vulnerability is deterministic and reachable through `position-nft::transfer` plus any owner-gated controller entrypoint.

### Recommendation
Make the spend path use the same authoritative source as `require_account_owner`: inside `require_owner_or_delegate` / `is_owner_or_delegate`, resolve `storage::account_owner(env, account_id)` (the live NFT owner) instead of the cached `Account.owner`, and evaluate delegates against that resolved owner. Alternatively, refresh `Account.owner` from the NFT on every `storage::get_account` load and assert consistency on write.

### Proof of Concept
1. Alice: `controller::supply(caller=alice, account_id=0, spoke_id=1, assets=[(USDC, 100_000e6)])` → `account_id = 1`, `Account.owner = alice`.
2. Alice: `position-nft::transfer(from=alice, to=bob, token_id=1)` — Bob now holds the NFT; `Account.owner` in controller storage is unchanged.
3. Alice: `controller::withdraw(caller=alice, account_id=1, withdrawals=[(USDC, 0)], to=Some(alice))` — `require_owner_or_delegate` sees `caller == account.owner` (alice) and releases the full collateral to alice.
4. Bob calls `controller::withdraw(caller=bob, account_id=1, …)` — reverts `NotAuthorized`, because `bob != account.owner`.

Caveat: this finding assumes `storage::get_account` returns `Account.owner` as stored at creation without re-resolving it against `storage::account_owner`; if the loader already syncs the field from the NFT, the bug reduces to inconsistency rather than an exploitable gap. The source divergence between the two checks in `account.rs` (lines 121 vs 145) is the concrete evidence that two different ownership sources are in play.

### Citations

**File:** contracts/controller/src/account.rs (L62-70)
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
```

**File:** contracts/controller/src/account.rs (L99-110)
```rust
    match guard {
        AccountGuard::Supply => require_spoke_match(env, &account, spoke_id),
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
        AccountGuard::Multiply => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
            assert_with_error!(env, account.mode == mode, GenericError::AccountModeMismatch);
        }
    }
```

**File:** contracts/controller/src/account.rs (L115-127)
```rust
pub(crate) fn is_owner_or_delegate(
    env: &Env,
    account_id: u64,
    caller: &Address,
    owner: &Address,
) -> bool {
    if caller == owner {
        return true;
    }
    let active_manager =
        storage::get_position_manager(env, caller).is_some_and(|config| config.is_active);
    active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
}
```

**File:** contracts/controller/src/account.rs (L143-147)
```rust
pub(crate) fn require_account_owner(env: &Env, account_id: u64, caller: &Address) -> AccountMeta {
    let meta = storage::get_account_meta(env, account_id);
    let owner = storage::account_owner(env, account_id);
    assert_with_error!(env, owner == *caller, GenericError::AccountNotInMarket);
    meta
```

**File:** contracts/controller/src/positions/supply.rs (L149-152)
```rust
    let mut account = storage::get_account(env, account_id);
    require_owner_or_delegate(env, account_id, caller, &account.owner);

    let recipient = to.unwrap_or_else(|| caller.clone());
```

**File:** scripts/permissionless_entrypoints.txt (L111-111)
```text
position-nft::transfer | caller-auth | INV-AUTH-02 | from.require_auth authorizes the move and the stock update rejects any from that is not the token owner, so only the holder can move the whole account; delegate grants from the previous owner go inactive.
```
