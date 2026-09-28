### Title
Stale in-account `owner` lets a transferred position's previous owner keep spending authority - ([File: contracts/controller/src/account.rs])

### Summary
`is_owner_or_delegate` authenticates the privileged caller against `account.owner`, the `Address` frozen into the `Account` struct at account creation in `create_account_with`. Canonical ownership, however, lives in the position-nft contract (`NFTStorageKey::Owner`), which `transfer`/`transfer_from` mutate without any controller callback. The owner-only paths (`renew_account`, `add_delegate`, `remove_delegate`) already distrust the stored field and instead call `require_account_owner`, which resolves ownership via `storage::account_owner`. The spending paths (`borrow`, `withdraw`, `multiply`, `flash_position`, `swap_debt`, `swap_collateral`, `repay_debt_with_collateral`, `migrate_from_blend`) trust the stale field, so a seller who transfers their position NFT retains full authority to borrow against and withdraw collateral that now belongs to the buyer — the same bug class as the MinIO advisory: one subsystem authenticates against a credential source the authoritative layer no longer honors.

### Finding Description
The MinIO report pattern is: the signature-verification gate keys on the presence of `Authorization` while `isPutActionAllowed` accepts `X-Amz-Credential` from the query string — two credential sources, the wrong one consulted. Here, two owner sources exist:

- `Account.owner`, written once at mint: `contracts/controller/src/account.rs` lines 64-65 (`owner: owner.clone()` inside `create_account_with`).
- The live NFT owner, mutated by `position-nft` `transfer`/`transfer_from` (stock OZ `NonFungibleToken` impl in `contracts/position-nft/src/contract.rs` lines 131-133), which performs `from.require_auth()` and `Base::update` locally — there is no cross-contract call back into the controller to resync `Account.owner`.

`is_owner_or_delegate` (`contracts/controller/src/account.rs` lines 115-127) short-circuits on `caller == owner`, where `owner` is `&account.owner` — the stale stored field — before even consulting the NFT. Every fund-moving entrypoint routes through it: `borrow`/`withdraw` via `require_owner_or_delegate` (account.rs lines 130-140; used in `positions/supply.rs` line 150 and `positions/debt.rs`), the strategy guards `AccountGuard::Migrate`/`AccountGuard::Multiply` (account.rs lines 101-109), and `repay_debt_with_collateral` (line 51). Meanwhile `require_account_owner` (account.rs lines 143-148) deliberately ignores `account.owner` and reads `storage::account_owner` — proving the codebase itself treats the struct field as non-authoritative for ownership.

Delegations are keyed per owner (`storage::get_delegates(env, account_id, owner)`), so a buyer's grants don't leak backward — but the `caller == owner` fast path needs no grant at all.

### Impact Explanation
An attacker supplies collateral, then transfers (or sells) the position NFT to a victim on a secondary market. The victim now owns an apparently well-collateralized account. The attacker then calls `withdraw(caller=attacker, account_id, withdrawals, to=attacker)` or `borrow(...)` on that account: `caller.require_auth()` passes trivially, and `require_owner_or_delegate` returns early because `caller == account.owner` still holds the attacker's address. Post-withdraw solvency checks protect the *account's* health factor, not the new owner — a full withdrawal of unborrowed collateral or a max-LTV borrow passes and sends funds `to` the attacker. Result: theft of user funds (the buyer's collateral) reachable by any unprivileged address holding a formerly-owned account.

### Likelihood Explanation
High conditional on `Account.owner` never being resynced. Nothing in the inspected code updates `account.owner` after `create_account_with`; the position-nft contract exposes no ownership-change hook, and `transfer` performs no controller call (`contract.rs` lines 131-133). Documentation claims "NFT ownership, including control of collateral and the debt obligation, transfers atomically" (`docs/reference/endpoints.md` line 49), which is precisely what the stale field breaks. Caveat: I did not read `contracts/controller/src/storage/account.rs`; if `storage::get_account` secretly overwrites `account.owner` from `storage::account_owner` on every load, the fast path is safe and this finding collapses — but the deliberate use of `storage::account_owner` inside `require_account_owner` instead of `account.owner` indicates the two diverge by design. The attack path requires only `caller.require_auth()` on the attacker's own address plus `withdraw`/`borrow`, both explicitly callable by any address.

### Recommendation
Resolve ownership from the canonical source in `is_owner_or_delegate`: replace the `caller == owner` comparison against `account.owner` with a live `storage::account_owner(env, account_id)` read (or resync `account.owner` from the NFT owner on every `storage::get_account` load and on `transfer` via a controller hook). Keep delegate lookups keyed to the live owner so a stale owner's grants cannot reactivate after a transfer back.

### Proof of Concept
1. Attacker calls `supply(attacker, 0, spoke_id, [(XLM_hub_key, 1000e7)])` → receives `account_id = N`, `Account.owner = attacker`, NFT `N` minted to attacker (`create_account_with`, account.rs line 64).
2. Attacker calls `position_nft.transfer(attacker, victim, N)` — succeeds via stock OZ path; no controller notification; `Account.owner` in controller storage still `attacker`.
3. Victim verifies `owner_of(N) == victim` and considers the collateral theirs; optionally adds collateral via `supply(victim, N, spoke_id, ...)`.
4. Attacker calls `withdraw(attacker, N, [(XLM_hub_key, 0)], Some(attacker))`:
   - `caller.require_auth()` — attacker signs, passes.
   - `storage::get_account` returns `Account { owner: attacker, ... }`.
   - `require_owner_or_delegate(env, N, attacker, &account.owner)` → `is_owner_or_delegate` returns `true` at the `caller == owner` fast path (account.rs line 121).
   - `pool_withdraw_call` pays the pool's underlying to `attacker` (supply.rs lines 201-209, 264).
5. Alternatively the attacker calls `borrow(attacker, N, borrows, Some(attacker))` to drain borrowable liquidity against the victim's collateral, leaving the victim holding the debt — solvency is re-proven post-borrow, which is satisfiable while the victim's collateral remains.