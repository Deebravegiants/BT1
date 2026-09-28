### Title
Stale `Account.owner` cached at mint is used for Multiply/Migrate authorization after the position NFT changes hands — prior owner and their delegates retain debt-minting power over the transferred account - (File: contracts/controller/src/account.rs)

### Summary
`--private-repos`-class desync: two components derive "who controls this account" from two different sources that are never reconciled. `require_account_owner` reads the live position-NFT owner via `storage::account_owner`, while `is_owner_or_delegate` / `require_owner_or_delegate` compare the caller against `account.owner` — an `Address` frozen into the `Account` struct at `nft_mint_call` time and never updated on NFT transfer. Because `load_or_create_account` uses `require_owner_or_delegate` for the `Migrate` and `Multiply` guards (`contracts/controller/src/account.rs:101-109`), the *original* minter — and every delegate stored under `get_delegates(account_id, old_owner)` — keeps authority over an account now owned by someone else.

### Finding Description
In `create_account_with` (`contracts/controller/src/account.rs:64-70`), the `Account` struct stores `owner: owner.clone()` at mint. The position NFT is a transferable token (`contracts/position-nft/src/contract.rs` `transfer`/`approve`), and the controller's authoritative ownership check `require_account_owner` (`account.rs:143-148`) reads `storage::account_owner`, which reflects the *current* NFT holder. But `is_owner_or_delegate` (`account.rs:115-127`) returns true when `caller == owner` where `owner` is the stale `account.owner`, and delegate lookup is `storage::get_delegates(env, account_id, owner)` keyed under that same stale address.

Concretely: Alice mints account NFT, grants delegate Bob via `add_delegate`, then sells/transfers the NFT to Carol. Nothing clears `account.owner` or Alice's delegate list (delegates are keyed per `(account_id, owner)`; Carol's grants live under a different key). Bob — an unprivileged address holding a stale grant — still passes `require_owner_or_delegate` for `AccountGuard::Multiply`, so `multiply` on Carol's account succeeds with Bob as `caller`.

### Impact Explanation
`multiply` mints new debt and supplies swapped proceeds as collateral *to Carol's account*. Bob chooses a maximal debt leg against Carol's existing collateral, driving her health factor below `1e18`. Bob then liquidates from a second address (`liquidate` is permissionless), repaying the debt he himself created and seizing collateral — including Carol's pre-existing collateral legs via the pro-rata multi-leg seizure — at the HF-based bonus. Net effect: theft of the buyer's collateral value bounded by the liquidation bonus, executed entirely through entrypoints in scope (`multiply`, `liquidate`, position-nft `transfer`/`approve`). The previous owner Alice herself can do the same, since `caller == account.owner` still passes. This is exactly the report's shape: the authorization source (cached owner/delegate key) diverges from the operative ownership source (live NFT owner) and the stale source is never invalidated.

### Likelihood Explanation
Trigger requires a position-NFT transfer of an account that has (a) a stored delegate or (b) an original owner willing to attack — both reachable by unprivileged addresses; `transfer` and `add_delegate` are normal user operations. Secondary markets or OTC sales of leveraged positions make dormant-delegate persistence realistic. Residual uncertainty: I verified the two ownership sources in `account.rs` but did not trace whether `multiply` caps debt such that HF can always be pushed under water, and whether `Account` is ever rewritten to resync `owner` on any path — no such resync was found in the code I read.

### Recommendation
Derive authorization and ownership from a single canonical source, mirroring the advisory's fix ("the authorized segment and the backend remote must derive from the same cleaned value"):

- In `load_or_create_account` / `require_owner_or_delegate`, resolve `owner` via `storage::account_owner(env, account_id)` (live NFT owner) instead of `account.owner`, or drop `Account.owner` entirely.
- In `set_account_delegate` / delegate storage, key delegate sets by `account_id` only (or re-key on ownership change) so grants do not survive a transfer under the seller's address.
- Optionally add a position-nft transfer hook that clears per-owner delegate entries, so authorization state cannot outlive the identity it was granted to.

### Proof of Concept
```text
1. Alice: supply() -> creates account_id=A, owner=Alice, collateral XLM.
   Alice: add_delegate(Alice, A, Bob)          // Bob is an active manager
   Alice: position-nft.transfer(Alice -> Carol, A)
   // storage::account_owner(A) == Carol; account.owner == Alice (stale)
   // get_delegates(A, Alice) still contains Bob.
2. Bob: multiply(caller=Bob, account_id=A, spoke_id=s, collateral=XLM_key,
                 debt=USDC_key, debt_amount=max, mode=Multiply, swap=route,
                 initial_payment=dust)
   // load_or_create_account -> AccountGuard::Multiply ->
   //   require_owner_or_delegate: is_owner_or_delegate reads
   //   get_delegates(A, account.owner=Alice) -> contains Bob -> PASS
   // Account now carries large USDC debt; HF < 1e18.
3. Bob2 (or Bob): liquidate(A, payments=[USDC leg], SeizeMode::Transfer)
   // repays Bob-minted debt, seizes Carol's XLM collateral at bonus -> profit.
```
Key code: `contracts/controller/src/account.rs:115-127` (`is_owner_or_delegate` on stale `account.owner`), `:98-109` (`AccountGuard::Migrate`/`Multiply` guards), `:64-70` (`owner` frozen at mint), `:143-148` (`require_account_owner` on live NFT owner — the divergent second source).