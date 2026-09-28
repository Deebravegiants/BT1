### Title
Stale stored account owner retains full spending authority after position-NFT transfer — old owner can drain the account - (File: contracts/controller/src/account.rs)

### Summary
The controller stores `owner` inside the `Account` struct at mint time and uses that stored value to authorize `borrow`, `withdraw`, and every strategy entrypoint via `is_owner_or_delegate` / `require_owner_or_delegate`. Account ownership, however, actually lives in the position-NFT, which is freely transferable. Nothing in the account-loading path restamps `Account.owner` from the current NFT holder, so after a transfer the *previous* owner still satisfies `caller == account.owner` while the *new* owner is rejected — a privilege-escalation analog of CVE-2020-8559's unvalidated redirect: authority follows a stale upstream identity instead of the real one.

### Finding Description
`create_account` mints the NFT to `owner` and persists `Account { owner: owner.clone(), ... }` at `contracts/controller/src/account.rs:62-70`. Spending authority is then decided by `is_owner_or_delegate`, whose first check is `caller == owner` against that *stored* field (`account.rs:121`), reached from `process_withdraw` (`positions/supply.rs:150`) and `process_borrow` via `require_owner_or_delegate` (`account.rs:130-140`).

Owner-only maintenance functions use a *different* source of truth: `require_account_owner` reads `storage::account_owner` (the live NFT holder) and compares it to the caller (`account.rs:143-148`). The explicit comment in `scripts/permissionless_entrypoints.txt:111` — "delegate grants from the previous owner go inactive" — confirms delegates are keyed under the stored owner and that the codebase treats NFT transfer as changing ownership, yet `Account.owner` is never rewritten in any transfer hook (the NFT contract cannot call back into the controller).

Result: after `position-nft::transfer`, the stored `account.owner` still names the seller. The seller can call `borrow`/`withdraw`/`swap_collateral`/`repay_debt_with_collateral(close_position=true)` on the sold account and route funds to themselves via the `to` argument. The buyer, despite holding the NFT, fails `caller == account.owner` on spending paths.

### Impact Explanation
Theft of user funds / permanent loss: a seller (or anyone who convinces a user to transfer the NFT — e.g., marketplace sale, gifting, or collateral-management handoff) retains complete control of the account's collateral and borrow capacity and can withdraw all supplied assets or max-borrow against them. The victim cannot even race, because the stored-owner check locks them out of the same entrypoints.

### Likelihood Explanation
Position NFTs are explicitly designed to be transferable (`position-nft::transfer`, `transfer_from`, `approve`, `approve_for_all` are stock entrypoints). Any secondary-market sale or wallet migration of an account NFT creates the precondition with no privileged action required. Medium likelihood, critical impact.

### Recommendation
Derive the owner at authorization time from `storage::account_owner` (live NFT holder) instead of the stored `Account.owner` field — i.e., make `is_owner_or_delegate`/`require_owner_or_delegate` resolve `owner` from the NFT on every call, or restamp `account.owner` inside `storage::get_account`. Alternatively, gate `position-nft::transfer` on controller approval so the controller can rotate `account.owner` and delegate keys atomically.

### Proof of Concept
1. Alice calls `supply(caller=alice, account_id=0, ...)` → account `A` created, NFT minted to Alice, `Account.owner = alice`.
2. Alice supplies 10,000 USDC collateral.
3. Alice calls `position-nft::transfer(alice → bob, token_id=A)` — succeeds, stock NFT logic.
4. `storage::account_owner(A)` now returns `bob`, but `Account.owner` still equals `alice`.
5. Alice calls `withdraw(caller=alice, account_id=A, withdrawals=[(USDC, 0)], to=Some(alice))`. `process_withdraw` → `require_owner_or_delegate(env, A, alice, &account.owner=alice)` passes (`account.rs:121,136`); the entire collateral pays out to Alice.
6. Bob's own `withdraw` reverts `NotAuthorized` at the same check.

Uncertainty note: I verified the two divergent owner sources in `account.rs` but could not exhaustively confirm within available iterations that no `get_account`/transfer path restamps `Account.owner`; the stored field is only written in `create_account` in all locations surfaced by search.