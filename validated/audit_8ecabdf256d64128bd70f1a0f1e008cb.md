### Title
Stale stored `account.owner` lets the previous NFT holder keep full account control after position transfer - (File: contracts/controller/src/account.rs)

### Summary
The position NFT is freely transferable (`position-nft` transfer/approve), but the controller authenticates account operations against the `owner` field stored in `Account` at creation time (`account.rs:64-70`), not against the live NFT owner. `require_owner_or_delegate` (`account.rs:130-140`) compares `caller == account.owner`, so after a sale/gift/transfer the *previous* owner — and their delegate list — retains full spending authority over the account, while the new NFT holder gains no authority at all. This mirrors the bug class of the report: an authority check resolves credentials in the wrong (broader/stale) scope.

### Finding Description
`create_account` stores `owner` inside `Account` and persists it; it is never resynced to `Base::owner_of` on NFT transfer. Two different owners are consulted:

- `require_owner_or_delegate(env, account_id, caller, &account.owner)` (account.rs:130) — used by `borrow`, `withdraw`, `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend` via `load_or_create_account`/`AccountGuard` (account.rs:99-110) — trusts the *stored* owner.
- `require_account_owner` (account.rs:143-148) — used only by `renew_account`/`add_delegate`/`remove_delegate` — trusts the *live* NFT owner via `storage::account_owner`.

Delegate entries are also keyed by the stored owner (`storage::get_delegates(env, account_id, owner)` at account.rs:126), so the old owner's delegates survive the transfer too. The new owner cannot even revoke them, because `remove_delegate` requires the *current* NFT owner, while `is_owner_or_delegate` validates the delegate against the *old* owner's list — a split-scope inconsistency.

### Impact Explanation
Theft of user funds. After acquiring a position NFT (purchase, OTC deal, or being sent one), the victim owns collateral the seller can still `withdraw` or `borrow` against, draining assets to the seller's benefit. The victim's NFT is economically worthless while the protocol reports them as owner. Scope confusion between stored credential and actual ownership directly enables ex-owner extraction of all collateral.

### Likelihood Explanation
Fully reachable by a single unprivileged address: any user holding a position NFT calls the standard OZ `transfer` on `position-nft`, then invokes `controller::withdraw` (or `borrow`) with the old `account_id`. `caller.require_auth()` passes (they sign), `require_owner_or_delegate` passes (stored owner unchanged), and post-pool risk gates only protect solvency, not ownership. No privileged actor, timing, or oracle dependency. Mitigating factor: victim must accept/use an NFT whose seller retains control, i.e., requires a secondary-market interaction, so Medium rather than High.

### Recommendation
Derive authority from the live NFT owner on every account-guarded entrypoint: replace use of `account.owner` in `require_owner_or_delegate`/`is_owner_or_delegate` with `storage::account_owner(env, account_id)` (as `require_account_owner` already does), and key delegate lists by `account_id` alone or by the current NFT owner, so transfers atomically re-scope owner and delegate authority.

### Proof of Concept
1. Alice calls `controller::supply` creating `account_id = 1` (NFT minted to Alice; `Account.owner = Alice`).
2. Alice sells the position: calls `position-nft::transfer(Alice → Bob, token_id=1)`. `Base::owner_of` now returns Bob; `Account.owner` still equals Alice.
3. Alice calls `controller::withdraw(caller=Alice, account_id=1, hub_asset, amount)`. `caller.require_auth()` succeeds; `require_owner_or_delegate` sees `caller == account.owner` (Alice) and passes; collateral is withdrawn to Alice.
4. Bob calls `controller::withdraw`; `require_owner_or_delegate` panics `NotAuthorized` despite Bob holding the NFT.
5. Bob also cannot call `remove_delegate` for Alice's stale delegates — `require_account_owner` passes for Bob, but the delegates were stored under Alice's owner key, so they remain active and Alice's manager can still act.