### Title
NFT transfer desynchronizes account ownership: stored `account.owner` retains spending authority while the new NFT holder is locked out — (File: contracts/controller/src/account.rs)

### Summary
The controller tracks two different notions of account ownership. Spending authority (`borrow`, `withdraw`, `multiply`, `swap_*`, `flash_position`, `migrate_from_blend`, Credit-seize receiver) is gated by `is_owner_or_delegate`, which compares the caller against `account.owner` — a field written once at account creation in `create_account_with` and never updated. Administrative authority (`renew_account`, `add_delegate`, `remove_delegate`) is gated by `require_account_owner`, which reads `storage::account_owner` — the *current* position-NFT owner. When the position NFT is transferred (a standard permissionless `transfer` on the position-nft contract), the NFT owner changes but `account.owner` does not. The previous owner keeps full spending power over the account's collateral and debt capacity, while the new NFT holder can only call the owner-only admin functions and cannot touch a single position.

### Finding Description
`create_account_with` stores `owner` inside the `Account` struct at mint time [1](#0-0) . Every value-moving guard resolves the caller against that stored field: `is_owner_or_delegate` returns true when `caller == owner` [2](#0-1) , and `require_owner_or_delegate` is invoked from `load_or_create_account` for the `Migrate` and `Multiply` guards [3](#0-2) , from the liquidation Credit-receiver path (`resolve_seize_receiver` uses `receiver.owner`, i.e., the stored owner, not the NFT owner) [4](#0-3) , and from the supply/debt position flows. Separately, `require_account_owner` explicitly "verifies that `caller` currently owns the account NFT" via `storage::account_owner` [5](#0-4) .

There is no path in `account.rs` that writes `account.owner` after creation, and the position-nft contract is a stock OpenZeppelin `NonFungibleToken` (the access-control gate pins its `transfer`/`approve` as plain `caller-auth` with no controller callback) [6](#0-5) . So a `position-nft::transfer` leaves `account.owner` permanently pointing at the seller.

The delegate list compounds the desync: delegates are stored under the *stored* owner's key (`storage::get_delegates(env, account_id, owner)` where `owner` is `account.owner`) [7](#0-6) , so delegates granted by the seller remain valid after the sale, while `set_account_delegate` only lets the *current NFT owner* mutate a delegate list keyed to the *seller* — the buyer cannot even clean up the seller's delegates, and can only add/remove entries under their own (buyer) owner key that `is_owner_or_delegate` will never consult for this account.

### Impact Explanation
- **Theft of user funds / economic value**: after selling or transferring the NFT, the seller (or any of the seller's still-active delegates) retains full `require_owner_or_delegate` authority — they can `withdraw` all collateral, `borrow` up to the LTV limit, or `swap_collateral`/`swap_debt` on an account they no longer own. Anyone who buys, receives, or takes custody of a position NFT acquires the token but zero spending control.
- **Permanent freezing of funds**: the new NFT owner fails `require_owner_or_delegate` on every position-mutating entrypoint, so they cannot withdraw, repay-debt-with-collateral, or migrate the position they nominally own. They also cannot accept Credit-mode liquidation proceeds (`resolve_seize_receiver` checks `receiver.owner`).
- This is the direct analog of the Deno class: the authorization check is performed against a stale, inner-recorded identity (`account.owner`) rather than the authoritative identity enforced at the outer layer (NFT ownership via `require_account_owner`), letting a party bypass the intended permission boundary after a legitimate state change.

### Likelihood Explanation
- `position-nft::transfer`/`transfer_from`/`approve` are stock permissionless entrypoints explicitly in scope; nothing requires NFT trades to be rare.
- The vulnerability triggers deterministically on the first transfer of any account NFT — no oracle condition, no timing race, no privileged action.
- No mitigation exists: the buyer has no entrypoint that resyncs `account.owner`, and the seller cannot be stripped of authority by the buyer (delegate revocation is keyed to the seller's owner record).

### Recommendation
Make the NFT the single source of truth for spending authority: have `is_owner_or_delegate`/`require_owner_or_delegate` resolve `storage::account_owner(env, account_id)` (current NFT owner) instead of the stored `account.owner` field, and key the delegate list to the account id (or re-derive the owner key from the NFT) so delegation follows the token. Alternatively, disable NFT transfers for accounts with open positions, but that sacrifices the transferability the NFT exists to provide.

### Proof of Concept
1. Alice calls `controller::supply` with `account_id = 0`; an account `A` is created with `account.owner = Alice` and NFT `A` minted to Alice.
2. Alice sells NFT `A` to Bob and calls `position-nft::transfer(Alice, Bob, A)`.
3. Bob calls `controller::withdraw`/`borrow` on `A`: `require_owner_or_delegate` compares `Bob` to `account.owner == Alice` → `NotAuthorized`. Bob is locked out of every position flow.
4. Alice calls `controller::withdraw` on `A`: `caller == account.owner` → succeeds, draining the collateral Bob paid for. Equivalently, an active delegate Alice registered before the sale can do the same.
5. Bob calls `add_delegate`/`remove_delegate`: authenticated as NFT owner, but mutations land under `owner = Bob` while `is_owner_or_delegate` only reads the delegate list under `owner = Alice`, so Bob cannot revoke Alice's surviving delegates.

*Caveat: I could not exhaustively confirm that no hook resyncs `account.owner` on NFT transfer (e.g., a custom `transfer` override in `position-nft/src/contract.rs` or a controller notifier); the pinned stock OpenZeppelin classification and the absence of any `account.owner` writer in `account.rs` strongly indicate none exists, but that file's full transfer implementation was not read.*

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

**File:** contracts/controller/src/account.rs (L101-109)
```rust
        AccountGuard::Migrate => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
        }
        AccountGuard::Multiply => {
            require_owner_or_delegate(env, account_id, caller, &account.owner);
            require_spoke_match(env, &account, spoke_id);
            assert_with_error!(env, account.mode == mode, GenericError::AccountModeMismatch);
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

**File:** contracts/controller/src/account.rs (L142-148)
```rust
/// Returns metadata after verifying that `caller` currently owns the account NFT.
pub(crate) fn require_account_owner(env: &Env, account_id: u64, caller: &Address) -> AccountMeta {
    let meta = storage::get_account_meta(env, account_id);
    let owner = storage::account_owner(env, account_id);
    assert_with_error!(env, owner == *caller, GenericError::AccountNotInMarket);
    meta
}
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L179-180)
```rust
    let receiver = storage::get_account(env, requested);
    account::require_owner_or_delegate(env, requested, liquidator, &receiver.owner);
```

**File:** scripts/check_access_control.py (L136-148)
```python
    "NonFungibleToken": {
        "transfer": "caller-auth",
        "transfer_from": "caller-auth",
        "approve": "caller-auth",
        "approve_for_all": "caller-auth",
        "balance": "view",
        "owner_of": "view",
        "get_approved": "view",
        "is_approved_for_all": "view",
        "name": "view",
        "symbol": "view",
        "token_uri": "view",
    },
```
