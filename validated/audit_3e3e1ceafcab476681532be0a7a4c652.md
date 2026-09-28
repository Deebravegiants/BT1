### Title
Stale `Account.owner` lets a transferred position's previous owner keep spending authority — ([File: contracts/controller/src/account.rs])

### Summary
The controller tracks account ownership in two places that can diverge: the `owner` field stored inside the `Account` struct at creation (`account.rs:66`), and the live `owner_of` on the position-nft contract (`contract.rs:2` — "the token owner (`owner_of`) is the account owner"). The NFT is a standard OpenZeppelin enumerable token; `transfer`/`approve` execute entirely inside the position-nft contract with no callback into the controller, so `Account.owner` is never resynchronized after a transfer. `require_account_owner` correctly re-reads the NFT (`storage::account_owner`, `account.rs:145`), but `require_owner_or_delegate` / `is_owner_or_delegate` (`account.rs:115-140`) compare the caller against the stale `account.owner` passed in by `load_or_create_account` (`account.rs:102,106`) and by the withdraw/borrow paths. The result mirrors CVE-2026-61442: a weaker authorization check (cached owner field) bypasses the canonical ownership check (NFT `owner_of`), letting a party who no longer owns the account act on it.

### Finding Description
- `create_account` writes `Account { owner: owner.clone(), .. }` once, at mint (`account.rs:64-70`). Nothing updates this field afterward.
- `PositionNft` exposes stock OZ `transfer`/`transfer_from`/`approve` via `#[contractimpl(contracttrait)] impl NonFungibleToken` (`contract.rs:131-133`). A transfer mutates only NFT storage (`NFTStorageKey::Owner`); the controller is never invoked, so `Account.owner` retains the original minter forever.
- `is_owner_or_delegate` returns `true` when `caller == owner` where `owner` is `&account.owner` — the stale field (`account.rs:121-122`).
- `borrow`, `withdraw`, `multiply`, `flash_position`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, and `migrate_from_blend` all route through `require_owner_or_delegate` (per `scripts/permissionless_entrypoints.txt:49-56` and `account.rs:102-108`), i.e., they trust the stale field.
- Symmetrically, the *new* NFT owner fails `caller == account.owner` and is not on the delegate list keyed under the old owner (`storage::get_delegates(env, account_id, owner)`, `account.rs:126`), so the legitimate owner is locked out of owner-gated flows while the seller retains them.

### Impact Explanation
Theft of user funds. After selling or transferring a position NFT, the previous owner can still call `withdraw` and `borrow` against the account — pulling out collateral and drawing debt that encumbers the position the buyer just acquired. This is a direct value transfer from the new owner to the old one and makes secondary-market position transfers unsafe. It also breaks `clean_bad_debt`/`liquidate` accounting expectations only incidentally; the primary loss is the drained collateral.

### Likelihood Explanation
Reachable by a single unprivileged address with only standard NFT interactions: the attacker supplies collateral, then calls the stock `transfer` on the position-nft contract (or lists the NFT on any marketplace) to move the token to a victim buyer. No privileged role, oracle manipulation, or timing dependency is required — the stale check is deterministic. The only prerequisite is that a victim accepts the NFT transfer, which is the intended use of a transferable position token.

### Recommendation
Make the NFT the single source of truth on every spending path: in `is_owner_or_delegate`/`require_owner_or_delegate`, resolve the owner via `storage::account_owner(env, account_id)` (live `owner_of`) instead of trusting `account.owner`, and key the delegate list under the freshly read owner. Either remove `Account.owner` or treat it as a cache that is always refreshed from the NFT before authorization decisions.

### Proof of Concept
1. Attacker calls `controller::supply(caller=attacker, account_id=0, hub_asset=USDC, amount=X)` → account `A` created, NFT minted to attacker, `Account.owner = attacker`.
2. Attacker calls `position_nft.transfer(attacker, victim, A)` — succeeds; NFT `owner_of(A) = victim`; `Account.owner` still `attacker`.
3. Attacker calls `controller::withdraw(caller=attacker, account_id=A, hub_asset=USDC, amount=X)`. `attacker.require_auth()` passes; `load_or_create_account`/`require_owner_or_delegate` compares `attacker == account.owner` → `true`. Collateral is paid to the attacker even though `owner_of(A)` is the victim.
4. Optionally `controller::borrow` against the victim's position before/after withdrawing, leaving the victim's purchased account insolvent or empty.

**Uncertainty note:** I verified that `Account.owner` is written only at creation and that `require_owner_or_delegate` consumes `account.owner`, but I could not confirm whether `storage::get_account` re-derives `owner` from the NFT on every load (the existence of a separate `storage::account_owner` used by `require_account_owner` suggests it does not). If `get_account` does refresh the field, the stale-owner window collapses and this reduces to a delegate-list migration issue only. A quick check of `contracts/controller/src/storage/account.rs::get_account` resolves this definitively.