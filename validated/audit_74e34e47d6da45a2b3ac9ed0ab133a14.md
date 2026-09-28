### Title
Stale cached `account.owner` grants post-transfer control — position authority is checked against the mint-time owner, not the current NFT holder - ([File: contracts/controller/src/account.rs](contracts/controller/src/account.rs))

### Summary
Every value-moving entrypoint that gates on account ownership (`withdraw`, `borrow`, `multiply`, `migrate_from_blend`, `swap_collateral`, `swap_debt`, `repay_debt_with_collateral`) authorizes the caller via `require_owner_or_delegate`, which compares the caller against `account.owner` — a field snapshotted into the `Account` struct at mint time in `create_account_with`. The true ownership primitive is the position NFT: `require_account_owner` / `renew_account` / `set_account_delegate` correctly resolve `storage::account_owner` (the NFT `owner_of`). Nothing in the transfer path rewrites `account.owner`, so the ownership check is validated against a stale credential rather than the live token — the direct analog of accepting a JWT without re-verifying its signature.

### Finding Description
- `create_account_with` stores `owner` inside `Account` at mint (`contracts/controller/src/account.rs:64-70`) and `load_or_create_account` returns that struct.
- `require_owner_or_delegate` (`account.rs:130-140`) and `is_owner_or_delegate` (`account.rs:115-127`) compare `caller` to `account.owner` and look up delegates keyed by that stored owner — never consulting the NFT.
- `process_withdraw` (`contracts/controller/src/positions/supply.rs:147-157`) calls `require_owner_or_delegate(env, account_id, caller, &account.owner)` and then pays out to `to` (any external recipient via `require_external_recipient`).
- `process_borrow` (`contracts/controller/src/positions/debt.rs:40-57`) does the same and disburses borrowed assets to an arbitrary `to`.
- Position-NFT `transfer`/`transfer_from` (reachable by any owner) moves the NFT but performs no callback into the controller to update `account.owner` or clear `get_delegates(account_id, owner)`.
- Contrast: `require_account_owner` (`account.rs:143-148`) does check `storage::account_owner` — used only for `renew_account`, `add_delegate`, `remove_delegate` — confirming the two notions of "owner" diverge and only the NFT one is canonical.

### Impact Explanation
After an account NFT is sold or transferred, the previous holder retains full owner-equivalent authority over the lending account: they can `withdraw` every supply position to themselves and `borrow` the maximum against the new owner's collateral to an arbitrary `to` address, until the post-borrow health-factor gate. The buyer acquires an NFT that controls nothing — `renew_account` and delegate management work for them, but all value-bearing operations still obey the seller. This is theft of user funds and unclaimed collateral value by a single unprivileged address, mirroring the advisory's authentication bypass where a stale/improperly validated credential is accepted as proof of identity.

### Likelihood Explanation
Reachable entirely by unprivileged addresses: victim calls position-nft `transfer`, then the seller (whose `Address` remains `account.owner`) calls `controller.withdraw(account_id, withdrawals, Some(attacker))` and/or `controller.borrow(account_id, borrows, Some(attacker))` with only their own signature. No privileged role, oracle manipulation, or timing edge is required — the only precondition is one ordinary NFT transfer, which is a documented supported entrypoint.

### Recommendation
Resolve ownership from the position NFT at the point of action: have `require_owner_or_delegate` (or its callers) use `storage::account_owner(env, account_id)` instead of `account.owner`, and key delegate storage to the current NFT owner. Alternatively, make NFT `transfer`/`transfer_from` invoke a controller hook that syncs `account.owner` and migrates/clears the delegate set, with an invariant test asserting that post-transfer the previous owner fails authorization on `withdraw`/`borrow`.

### Proof of Concept
1. Alice supplies USDC via `supply(caller=alice, account_id=0, spoke_id, [USDC])`; account NFT `id=1` mints to Alice and `account.owner = alice`.
2. Alice calls `position_nft.transfer(alice, bob, 1)` (or `approve` + `transfer_from`). The NFT now belongs to Bob; `account.owner` still equals `alice`.
3. Alice calls `controller.withdraw(account_id=1, withdrawals=[(USDC, 0)], to=Some(alice))`. `process_withdraw` passes `require_authorized_caller` (Alice signs) and `require_owner_or_delegate` (`caller == account.owner`), and the pool pays Alice the full position.
4. Symmetrically, Alice calls `controller.borrow(1, [(ETH, max)], Some(alice))`, drawing debt against collateral Bob believes he owns.
5. Bob, the legitimate NFT owner, cannot withdraw or borrow: `require_owner_or_delegate` rejects him because `bob != account.owner` and he is absent from `get_delegates(1, alice)`.