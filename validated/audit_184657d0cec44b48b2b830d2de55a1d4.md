### Title
Controller authorizes position management against a stale `account.owner` recorded at mint time instead of the live position-NFT owner, letting a previous owner keep control after transfer - (File: contracts/controller/src/account.rs)

### Summary
The libp2p advisory is about accepting a record whose claimed identity (`PeerId`) was never checked against the key that actually authorized it. The controller has the same shape: it keeps an `owner: Address` field inside the `Account` struct written once at mint, and all sensitive position entrypoints (`borrow`, `withdraw`, `multiply`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend`, `flash_position` on an existing account) authorize via `is_owner_or_delegate`/`require_owner_or_delegate`, which compare `caller` to that stored field — not to the current owner of the position NFT that `require_account_owner` reads via `storage::account_owner` for `renew_account`/`add_delegate`/`remove_delegate`.

### Finding Description
`create_account` mints the NFT and persists `Account { owner: owner.clone(), .. }` (account.rs:62-71). Every position-mutating guard then resolves identity from that stored field:

```rust
// contracts/controller/src/account.rs
if caller == owner { return true; }              // owner = account.owner, set at mint
let active_manager = storage::get_position_manager(env, caller)...;
active_manager && storage::get_delegates(env, account_id, owner).contains(caller)
```

A different function, `require_account_owner`, validates identity against `storage::account_owner(env, account_id)` — the NFT contract's current `owner_of` — and is used only for TTL renewal and delegate management. That dual-source design means `Account.owner` and the NFT's live owner can diverge when the position NFT is transferred (`transfer`/`approve` are in-scope entrypoints on the position-nft contract). Unless an explicit hook rewrites `account.owner` on every NFT transfer — no such synchronization is visible in `account.rs`, and I could not confirm one exists in `storage.rs` — the address recorded in the account record remains authoritative for value-moving calls regardless of who actually holds the NFT.

Note on certainty: I verified both ownership sources in `account.rs` but did not get to read `contracts/position-nft/src/contract.rs` `transfer` or `storage.rs` to confirm whether `account.owner` is updated on transfer. If a sync hook exists there, the concrete exploit below is invalid.

### Impact Explanation
If `account.owner` is not resynchronized on NFT transfer, the seller/previous owner of a position NFT retains full owner authority over the account: they can call `borrow(account_id, ..., to: attacker)` to draw debt against collateral the buyer paid for, or `withdraw` up to the solvency limit — direct theft of the buyer's collateral value. Symmetrically, the buyer (the live NFT owner) is *not* recognized by `is_owner_or_delegate`, so the true owner cannot borrow, withdraw, add delegates, or rescue the position — permanent freezing of funds for the victim combined with theft by the seller. The delegate list is also keyed to the stale `account.owner` (`get_delegates(env, account_id, owner)`), so delegate grants made by the buyer under their own address would never authorize anyone for the account.

### Likelihood Explanation
Triggering requires only a position-NFT transfer, which is a normal supported operation. On a secondary market, a seller lists a valuable leveraged account, the buyer pays, and the seller then calls `borrow`/`withdraw` naming the `account_id` — the stored `owner` still matches the seller's address, so `require_owner_or_delegate` passes with a single signature. No privileged role, oracle manipulation, or timing dependence is involved.

### Recommendation
Bind every authorization decision to the authoritative identity source. Replace uses of the stored `account.owner` in `is_owner_or_delegate`/`require_owner_or_delegate` with `storage::account_owner(env, account_id)` (the live NFT `owner_of`), exactly as `require_account_owner` already does — or delete the redundant `Account.owner` field entirely so there is only one identity. If the field is kept for caching, require a controller-mediated ownership hook invoked by the position-NFT contract on every `transfer`/`burn` that rewrites `account.owner` and re-keys the delegate map.

### Proof of Concept
1. Alice calls `supply` with `account_id = 0`; `create_account` mints position NFT `id = N` and stores `Account.owner = Alice`.
2. Alice borrows to build a leveraged position, then sells/transfers NFT `N` to Bob via the position-nft `transfer`.
3. `storage::account_owner(N)` now returns Bob, but `Account.owner` still equals Alice unless a sync hook rewrites it.
4. Alice calls `controller.borrow(Alice, N, borrows, to: Alice)` — `require_owner_or_delegate` compares `Alice == account.owner` → passes → pool cash goes to Alice against collateral Bob now owns.
5. Bob calls `withdraw(Bob, N, ...)` — `Bob != account.owner` and Bob is not a delegate under `get_delegates(N, Alice)` → `NotAuthorized`. Bob's collateral is frozen and already encumbered by Alice's new debt.