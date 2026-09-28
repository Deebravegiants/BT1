### Title
Stale delegate grant silently reactivates when the account NFT returns to the granting owner, letting an old delegate drain the account - (File: contracts/controller/src/storage/account.rs)

### Summary
CVE-2019-3689 is a shared-location ownership flaw: a low-privilege principal (`statd`) owns a directory where root-managed files live, so it can trick privileged code into overwriting arbitrary files. The XOXNO analog is the account's `Delegates` storage entry: a `DelegateGrant` is stamped with the *granting* owner's address, survives NFT transfers, and is re-trusted the moment the NFT returns to that owner. A dormant delegate — a position manager the original owner authorized once — regains full economic control over the account without any fresh authorization, and can borrow or withdraw to an arbitrary recipient, including itself.

### Finding Description
`get_delegates` loads `ControllerKey::Delegates(account_id)` and filters on `grant.granted_by == *owner`, so a grant written by owner Alice is invisible while Bob holds the NFT but remains in storage (`contracts/controller/src/storage/account.rs:174-199`). Nothing clears the grant on transfer; `remove_delegate` deletes a stale grant only if an intervening owner explicitly calls it (`storage/account.rs:226-247`). `is_owner_or_delegate` then re-trusts the revived grant the instant `owner_of` resolves back to Alice (`contracts/controller/src/account.rs:114-127`).

Once trusted, the delegate passes `require_owner_or_delegate` in `process_borrow`, which sends proceeds to `to.unwrap_or(caller)` — an arbitrary external recipient chosen by the delegate (`contracts/controller/src/positions/debt.rs:31-57`). The same applies to `withdraw`, `swap_collateral`, `repay_debt_with_collateral`, `multiply`, `flash_position` and `migrate_from_blend`, all gated only by `require_owner_or_delegate`. A test confirms the delegate can borrow to itself (`tests/test-harness/tests/controller/borrow.rs:253-281`), and the threat model concedes delegates "can borrow/withdraw to their chosen recipient" and that a grant "can revive if the NFT returns before an intervening owner updates delegates" (`docs/explanation/threat-model.md:81-87`).

The trap: NFT `transfer`/`transfer_from`/`approve` are permissionless for the token holder, account NFTs are freely tradable, and an interim owner has no incentive to purge a grant that doesn't threaten them. The original owner cannot revoke while someone else holds the NFT (`set_account_delegate` requires `require_account_owner`, `account.rs:242-264`), so the grant becomes a loaded gun that fires the moment the NFT returns — including the same-transaction round trip.

### Impact Explanation
Theft of user funds. A revived delegate can call `borrow(caller=delegate, account_id, borrows, to=Some(delegate))`, minting maximum debt against the victim's collateral and taking the proceeds; it can also `withdraw` free collateral to itself up to the solvency floor. The victim is left with a debt obligation and stripped borrowing capacity. Because the account's solvency gates check the account, not the recipient, the full LTV-weighted collateral value is extractable.

### Likelihood Explanation
Requires (a) the victim previously delegated to a still-active registered position manager, and (b) the NFT to leave and return to the victim without an interim owner calling `remove_delegate`. Both are realistic: position managers are designed as shared infrastructure across many accounts, NFT transfers are the intended way to sell positions, and interim owners gain nothing from purging someone else's stale grants. The delegate needs no further authorization — `require_auth` is on its own address.

### Recommendation
Invalidate grants at transfer time rather than lazily: burn/overwrite `ControllerKey::Delegates(account_id)` inside the controller's transfer flow, or stamp each grant with a monotonically increasing transfer epoch (stored in `AccountMeta` and bumped by a controller hook invoked from `position-nft` transfers) so `granted_by` alone cannot reactivate authority across an ownership round trip.

### Proof of Concept
```rust
// Alice owns account_id and delegates to MANAGER (an active approved manager).
t.supply(ALICE, "USDC", 100_000.0);
let account_id = t.account_id(ALICE);
t.enable_delegate(ALICE, "MANAGER", account_id);

// Alice sells/transfers the NFT to Bob. Bob never calls remove_delegate
// (the stale grant cannot hurt him — lookups use his owner key).
t.nft_transfer(ALICE, BOB, account_id);

// Bob sells the NFT back to Alice. get_delegates(account_id, ALICE) now
// returns the original grant — MANAGER is trusted again with no fresh auth.
t.nft_transfer(BOB, ALICE, account_id);

// MANAGER borrows up to the LTV limit and pays the proceeds to itself,
// loading Alice's account with debt it never authorized.
t.borrow_as_to("MANAGER", account_id, "ETH", /* up to LTV */, "MANAGER");
// MANAGER can additionally withdraw all non-debt-locked collateral to itself.
t.withdraw_as_to("MANAGER", account_id, "USDC", /* free amount */, "MANAGER");
```
Supporting evidence that revival is intended-to-be-blocked-but-incomplete: `remove_delegate` explicitly deletes stale grants "preventing those grants from reactivating if the NFT returns to their original owner" (`storage/account.rs:224-238`) — proving the revival path is real and only closes if an interim owner acts.