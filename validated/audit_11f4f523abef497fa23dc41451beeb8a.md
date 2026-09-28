### Title
`supply` credits a caller-funded deposit to `account_id` without an expected-owner check, so a transaction delayed in the mempool can fund an account whose NFT has since been transferred — (File: contracts/controller/src/account.rs)

### Summary
The reported bug class is "a caller submits a transaction whose effect is anchored to mutable global/current state (the current round counter) rather than to an explicit parameter or deadline; mempool delay changes *what* the transaction actually does." In XOXNO Lending, the same shape exists in `Controller::supply`: a caller authorizes a token pull and names only `account_id` and `spoke_id`, but the account-load path for `Supply` never checks that `caller` still owns (or is even related to) the target account. Between submission and execution the position NFT — which is freely transferable and carries the entire account — can change hands, and the delayed `supply` then irreversibly credits the caller's tokens to a different owner's account.

### Finding Description
`load_or_create_account` in `contracts/controller/src/account.rs` dispatches on `AccountGuard`. For `AccountGuard::Supply` the only check applied to an existing `account_id` is `require_spoke_match` — there is no call to `require_owner_or_delegate` or `require_account_owner`, unlike `Migrate` and `Multiply` which both require `caller` to be the owner or an active delegate: [1](#0-0) 

`require_account_owner` exists and is used elsewhere (e.g., `renew_account`, `set_account_delegate`), proving the contract has the ownership-check primitive but deliberately omits it on the supply path: [2](#0-1) 

Ownership of an account is purely a function of who holds the position NFT at execution time (`nft_try_owner_of_call` / `storage::account_owner`), and the NFT is a transferable/approvable asset, so the effective "target owner" of a `supply` call is mutable global state — exactly like `roundsCount` in the reference report. `supply` pulls real tokens from `caller` via `caller.require_auth()` and mints RAY supply shares into `account_id`'s positions; once credited, only the current NFT owner (or their delegate) can withdraw them.

### Impact Explanation
A user's pending `supply` transaction executes after the position NFT for `account_id` has been sold or transferred (a normal NFT marketplace trade or an `approve`/`transfer` on the position-nft contract). The caller's tokens are pulled and credited as collateral to an account they no longer control. Withdrawing requires `require_owner_or_delegate` against the *current* owner, so the supplier cannot recover the deposit: this is permanent loss / theft of user funds, matching the "wrong rounds get cancelled → irreversible effect on unintended target" shape of the reference issue.

### Likelihood Explanation
The trigger requires only a pending `supply` transaction and an intervening NFT transfer — both routine unprivileged actions (NFT `transfer`/`approve` are in-scope). Soroban transactions can sit in the mempool or be resubmitted across the transaction's validity window, and NFT trades settle atomically in other transactions. No privileged role, oracle manipulation, or flash infrastructure is needed. The scenario is realistic for accounts listed on secondary markets where the seller forgets (or cannot cancel) an in-flight supply. Likelihood is moderate, which is consistent with a Medium severity rather than High.

### Recommendation
Anchor the deposit to the state the caller saw at submission, mirroring the report's `startRoundId` recommendation. Either:

- Add an `expected_owner: Address` parameter to `supply` (and any other entrypoint that loads an account via `AccountGuard::Supply`), and revert if `storage::account_owner(env, account_id) != expected_owner`, or
- Require `caller == account owner || active delegate` on the `Supply` guard — i.e., use `require_owner_or_delegate` as `Migrate`/`Multiply` already do — so third-party top-ups are only possible through an explicit delegation, or
- If permissionless top-up is intentional, expose a separate `supply_to(account_id)` entrypoint that cannot reuse `account_id == 0` creation semantics, so a delayed owner-intent transaction and a deliberate donation are distinguishable.

### Proof of Concept
1. Alice owns position NFT `account_id = 7` (spoke 1) and lists it for sale.
2. Alice submits `controller.supply(caller=alice, account_id=7, spoke_id=1, assets=[(hub_asset, 1000 USDC)])`; the transaction stalls in the mempool.
3. Bob purchases NFT `7` via `position_nft.transfer`/`approve`+`transfer_from`; `storage::account_owner(7)` now returns Bob.
4. Alice's `supply` executes: `load_or_create_account` hits the `Supply` guard, passes `require_spoke_match`, pulls 1000 USDC from Alice, and credits scaled supply shares to account 7.
5. Bob (current owner) can `withdraw` or `borrow` against the new collateral. Alice has no recovery path — `withdraw` would revert `NotAuthorized` for her.

Caveat: if permissionless third-party supply is an explicit documented design decision, this reduces to a UX/footgun rather than a protocol flaw; the audit still holds because the silent loss arises from *caller intent* drifting between submission and execution, identical in mechanism to the reference `cancel` issue.

### Citations

**File:** contracts/controller/src/account.rs (L99-111)
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
    (account_id, account)
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
