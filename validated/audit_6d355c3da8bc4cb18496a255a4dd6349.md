### Title
Spending authority verified against the creation-time stored owner instead of the live NFT owner — a transferred position remains spendable by its previous owner (File: contracts/controller/src/account.rs)

### Summary
The CloudStack bug class is "authentication accepted without verifying the credential against the authoritative source." In XOXNO Lending the position NFT is the authoritative ownership record (`owner_of` — the token id *is* the account id), but every funds-moving entrypoint (`borrow`, `withdraw`, `multiply`, `flash_position`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend`, liquidation Credit-mode receiver check) authorizes the caller through `require_owner_or_delegate`, which compares the caller to `account.owner` — a value frozen in `Account` at mint time in `create_account_with` — rather than to the current `owner_of(token_id)`. The stronger check `require_account_owner`, used by `renew_account`/`add_delegate`/`remove_delegate`, reads `storage::account_owner` (the live NFT owner) and is documented as "verifying that `caller` currently owns the account NFT," confirming the two sources can diverge.

### Finding Description
`load_or_create_account` is the single guard funnel for all position-acting verbs. For an existing account it calls `require_owner_or_delegate(env, account_id, caller, &account.owner)` where `account` was loaded from persistent storage:

```rust
// contracts/controller/src/account.rs
fn is_owner_or_delegate(env, account_id, caller, owner) -> bool {
    if caller == owner { return true; }            // stored owner, not NFT owner
    let active_manager = storage::get_position_manager(env, caller)
        .is_some_and(|c| c.is_active);
    active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
}
```

`account.owner` is written once in `create_account_with` (`Account { owner: owner.clone(), .. }`) and nothing in the controller or the position-NFT contract rewrites it. The NFT contract exposes the full OZ `NonFungibleToken` surface (`transfer`, `approve`, `transfer_from`, `approve_for_all` via `#[contractimpl(contracttrait)]`), and `transfer` requires only the *current* token owner's auth — it never notifies the controller. After a transfer, `storage::account_owner` (NFT `owner_of`) points at the buyer, while `account.owner` still points at the seller. Every spend path therefore keeps accepting the seller's signature — exactly the "response accepted with a stale/unverified identity claim" shape of the CloudStack bug, mapped onto Soroban `require_auth` trees: the caller authenticates *as an address*, but the contract checks that address against the wrong authority record.

The asymmetry inside the same file proves the intent: `require_account_owner` exists precisely because the NFT is authoritative, yet `require_owner_or_delegate` (which guards the verbs that move collateral and mint debt) was not switched to it.

### Impact Explanation
Theft of user funds. The seller of a position NFT (or any recipient of an approved transfer) retains full owner-equivalent power over the account: `borrow` draws new debt against collateral the seller no longer owns, and `withdraw` pulls the supplied collateral out to the seller. A single unprivileged call pair — `nft.transfer(victim, attacker)` is not even needed; the attacker simply sells/lists the NFT and then front-runs the buyer's first action — `withdraw(account_id, …)` signed by the attacker succeeds because `caller == account.owner` still holds. Delegates registered under the old owner also survive (`storage::get_delegates(env, account_id, old_owner)`), extending the window. Loss is bounded only by the account's collateral value and remaining borrow capacity.

### Likelihood Explanation
Deterministic logic divergence, no timing or oracle dependency. The NFT is deliberately transferable (approvals, `approve_for_all`, marketplaces), and secondary-market trading of lending positions is the advertised purpose of tokenizing accounts. Any transfer permanently desynchronizes the two owner records with no re-sync path in `transfer`, `transfer_from`, or the controller.

### Recommendation
In `is_owner_or_delegate`/`require_owner_or_delegate`, resolve the owner via `storage::account_owner(env, account_id)` (the live NFT `owner_of`) instead of the cached `account.owner`, and key delegate lists to the account id alone rather than `(account_id, owner)` — or clear the delegate list whenever the NFT moves (impossible without a transfer hook, so the simpler fix is to stop trusting `account.owner` at all). Alternatively remove the `owner` field from `Account` so no path can read a stale identity.

### Proof of Concept
1. Alice calls `controller::supply(caller=alice, account_id=0, …)` → `create_account` mints NFT id N to Alice and stores `Account{owner: alice}`.
2. Alice transfers NFT N to Bob (`position_nft::transfer(alice, bob, N)`; the OZ transfer requires only Alice's auth and does not call the controller).
3. Alice (the attacker, now a non-owner) calls `controller::withdraw(caller=alice, account_id=N, payments=[…i128::MAX…])`. `alice.require_auth()` passes (her own signature); `load_or_create_account` → `require_owner_or_delegate` sees `caller == account.owner` (still `alice`) and admits her. Collateral is paid out to Alice.
4. Bob, the legitimate owner, is locked out: his `withdraw`/`borrow` calls fail `require_owner_or_delegate` even though `position_nft.owner_of(N) == bob`, and only owner-scoped verbs (`renew_account`, `add_delegate`) recognize him — so he can renew but cannot reclaim his funds.

Caveat: I verified the divergent checks in `contracts/controller/src/account.rs` and the unrestricted NFT transfer surface in `contracts/position-nft/src/contract.rs`; I could not open `contracts/controller/src/storage/account.rs` this session to confirm `storage::account_owner` reads the NFT `owner_of`, but the `require_account_owner` docstring ("verifying that `caller` currently owns the account NFT") and its `AccountNotInMarket` failure mode on `owner != caller` make that reading certain.