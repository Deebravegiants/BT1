### Title
Stale `Account.owner` grants post-transfer spending authority — an account's original owner retains owner privileges after selling the position NFT - (File: contracts/controller/src/account.rs)

### Summary

`is_owner_or_delegate` authenticates the caller against `Account.owner`, the owner address frozen into the account struct at mint time, rather than the live position-NFT holder. Entrypoints that load the account via `load_or_create_account` (multiply, flash_position, migrate_from_blend) and the debt/supply paths that call `require_owner_or_delegate(env, account_id, caller, &account.owner)` therefore accept the *previous* holder's signature as if it were the current owner's — the on-chain analogue of authenticating a user whose password was already changed.

### Finding Description

`Account` is created with `owner` stored at mint in `create_account_with` (account.rs:64-70). When an existing account is loaded, `load_or_create_account` passes `&account.owner` to `require_owner_or_delegate` (account.rs:98-109). Inside `is_owner_or_delegate`, the first check is `caller == owner` → `true` (account.rs:121-123), and the delegate list is keyed by that same stored `owner` (`storage::get_delegates(env, account_id, owner)`, account.rs:126).

The contract itself treats the NFT owner, not this stored field, as the source of truth: `require_account_owner` resolves the owner through `storage::account_owner(env, account_id)` (the NFT `owner_of`) and compares that to the caller (account.rs:143-148). The existence of a separate live-owner lookup confirms `Account.owner` is not authoritative — yet `require_owner_or_delegate` never consults it. After the NFT is transferred (`position-nft::transfer`, permissionless for the holder), `Account.owner` is not restamped, so:

- The seller still satisfies `caller == account.owner` and keeps full owner authority: `borrow`, `withdraw`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `multiply`, `flash_position`, `migrate_from_blend`.
- Delegates granted by the seller are keyed under the stale `owner` and also remain accepted by `get_delegates(env, account_id, owner)`.

### Impact Explanation

A seller lists/transfers a funded account NFT (collateral worth X). The buyer pays for the position; the seller then calls `controller::withdraw(account_id, hub_asset, amount, to: seller)` signed by themselves — `caller.require_auth()` passes (it is genuinely the seller signing) and `is_owner_or_delegate` passes against the stale `account.owner`. Collateral belonging to the buyer is drained to the seller: direct theft of user funds, Critical. The same path lets the ex-owner `borrow` against the buyer's collateral, burdening the account with debt while taking the proceeds.

### Likelihood Explanation

Fully unprivileged and deterministic: the attacker needs only to have once owned (or controlled a delegate of) the account. Position-NFT transfers are a supported, permissionless flow, so the trigger (transfer → stale owner → spend) requires no privileged action, timing, or price manipulation. The residual uncertainty is whether `storage::get_account` silently resyncs `Account.owner` from the NFT on load — nothing in `load_or_create_account` or `is_owner_or_delegate` performs that resync, and the separate `storage::account_owner` lookup in `require_account_owner` indicates the struct field is trusted nowhere else.

### Recommendation

In `require_owner_or_delegate` / `is_owner_or_delegate`, resolve the owner as `storage::account_owner(env, account_id)` (live NFT owner) instead of trusting the passed-in `account.owner`, and key delegate lookups under the live owner. Alternatively, remove `owner` from the `Account` struct entirely so no stale credential can be consulted.

### Proof of Concept

1. Alice calls `controller::supply` with `account_id = 0`, creating account `A` owned by Alice with `account.owner = Alice`, and supplies 10,000 USDC collateral.
2. Alice calls `position-nft::transfer(Alice → Bob, token_id = A)`. Bob is now `owner_of(A)`; `Account.owner` still stores Alice.
3. Alice calls `controller::withdraw(caller=Alice, account_id=A, hub_asset=USDC, amount, to=Alice)` and signs as herself.
4. `caller.require_auth()` succeeds (Alice's own signature); `require_owner_or_delegate` compares `caller == account.owner` → `Alice == Alice` → passes, despite Alice no longer holding the NFT.
5. Post-withdraw solvency check passes (Alice may instead `borrow` to the max LTV first, then withdraw proceeds as a delegate-funded recipient, or simply withdraw supplied collateral that is not locked against existing debt). Bob's collateral is transferred to Alice.

```text
expected:  step 3 reverts NotAuthorized (Alice is not the NFT owner)
actual:    is_owner_or_delegate returns true on the stale stored owner,
           and Bob's collateral leaves the pool
```