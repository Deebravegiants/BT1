### Title
Stale `Account.owner` lets a previous NFT holder retain spending authority after `transfer` - (File: contracts/controller/src/account.rs)

### Summary
The position NFT (`PositionNft`) is the live source of account ownership — `storage::account_owner` reads `owner_of` — but spending authorization in the controller flows through `require_owner_or_delegate(env, account_id, caller, &account.owner)`, where `account.owner` is a snapshot stored inside the `Account` struct at creation time [1](#0-0) . The NFT's `transfer`/`approve` are stock OpenZeppelin enumerable operations with no callback into the controller, so nothing re-stamps `Account.owner` when the token moves [2](#0-1) . The result mirrors CVE-2023-29868's incorrect-access-control shape: a principal (the former NFT owner, or a delegate granted by them) retains privileges over a resource that changed hands.

### Finding Description
- `load_or_create_account` with `AccountGuard::Migrate`/`Multiply` calls `require_owner_or_delegate(env, account_id, caller, &account.owner)` [3](#0-2) .
- `is_owner_or_delegate` first checks `caller == owner` against that stored snapshot, then consults `get_delegates(env, account_id, owner)` — the delegate list keyed by the *stored* owner [4](#0-3) .
- `require_account_owner`, by contrast, correctly resolves `storage::account_owner` (the live NFT owner) — proving the codebase has two distinct notions of "owner" [5](#0-4) .
- `PositionNft` implements `NonFungibleToken`/`NonFungibleEnumerable` verbatim with no `transfer` override or controller notification; ownership changes are invisible to `Account` state [6](#0-5) .
- The unit test `transfer_revokes_prior_owner_and_delegates` only re-checks `is_owner_or_delegate` against `storage::account_owner` (the *new* owner, `bob`); it never asserts that the `Account.owner` field was resynced, so a stale `account.owner = alice` would pass the test [7](#0-6) .

Caveat: I was unable to read `contracts/controller/src/storage/account.rs` (index excerpt unavailable) to confirm whether `get_account` resyncs `owner` from the NFT on load. If it does not, the stale-owner path below applies; if it silently resyncs, this finding collapses.

### Impact Explanation
If `Account.owner` is a creation-time snapshot: after the victim sells or transfers the position NFT, the previous owner (or any active manager the previous owner delegated) can still call `withdraw`, `borrow`, `multiply`, `swap_collateral`, `repay_debt_with_collateral`, `flash_position`, etc. on `account_id`, because `caller == account.owner` still holds for them. They can withdraw the victim's collateral (up to the solvency bound) or borrow against it, draining the position the buyer paid for — theft of user funds. Worse, the *new* owner `bob` fails `require_owner_or_delegate` (he equals neither `account.owner` nor a delegate listed under `alice`), so his funds are permanently frozen until the account is emptied by the stale owner.

### Likelihood Explanation
A single unprivileged address triggers this via `position-nft::transfer` (in-scope per the rules) followed by ordinary controller calls from the seller's key. No privileged role, no oracle manipulation, no race required — just the standard secondary-market flow the NFT exists to support. Delegate grants stored under the old owner in `get_delegates(account_id, alice)` equally survive, since the delegate set is keyed by the stale owner.

### Recommendation
Remove the stored `Account.owner` field entirely, or resync it from `storage::account_owner` inside `storage::get_account` / `load_or_create_account` before any guard runs; and key the delegate map by `account_id` alone (or by the live NFT owner) so grants die with the transfer.

### Proof of Concept
1. Alice supplies 10,000 USDC via `controller::supply(caller=alice, account_id=0, ...)` → account `A` minted, `Account.owner = alice`, NFT `A` owned by alice.
2. Alice calls `position-nft::transfer(alice, bob, A)`. NFT owner is now bob; `Account.owner` remains `alice` (no hook ran).
3. Alice calls `controller::withdraw(caller=alice, account_id=A, withdrawals=[(USDC, all)], to=Some(alice))`. `load_or_create_account` → `require_owner_or_delegate(env, A, alice, &account.owner=alice)` passes; the post-withdraw solvency check sees no debt, so the pool transfers bob's collateral to alice.
4. Bob's subsequent `withdraw`/`borrow` reverts with `NotAuthorized` (he is not `account.owner` and holds no delegate grant under alice).

### Citations

**File:** contracts/controller/src/account.rs (L98-112)
```rust
    let account = storage::get_account(env, account_id);
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
    (account_id, account)
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

**File:** contracts/controller/src/account.rs (L143-148)
```rust
pub(crate) fn require_account_owner(env: &Env, account_id: u64, caller: &Address) -> AccountMeta {
    let meta = storage::get_account_meta(env, account_id);
    let owner = storage::account_owner(env, account_id);
    assert_with_error!(env, owner == *caller, GenericError::AccountNotInMarket);
    meta
}
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

**File:** contracts/controller/tests/helpers/account.rs (L420-432)
```rust
    env.as_contract(&contract_id, || {
        let owner = crate::storage::account_owner(&env, account_id);
        assert_eq!(owner, bob);
        // Old owner and the grant they made are both dead.
        assert!(!is_owner_or_delegate(&env, account_id, &alice, &owner));
        assert!(!is_owner_or_delegate(&env, account_id, &manager, &owner));
        // New owner works, and a fresh grant by the new owner works.
        assert!(is_owner_or_delegate(&env, account_id, &bob, &owner));
        assert!(crate::storage::add_delegate(
            &env, account_id, &bob, &manager
        ));
        assert!(is_owner_or_delegate(&env, account_id, &manager, &owner));
    });
```
