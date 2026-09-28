### Title
Position-map storage keys can expire independently of account metadata, silently zeroing recorded debt and unlocking collateral withdrawal - ([File: contracts/controller/src/storage/account.rs])

### Summary
Analogous to CVE-2021-46909 — where code initialized once (`__init`) was dereferenced after the init window closed — the controller assumes that per-account persistent entries written at account/position creation remain readable forever. `ControllerKey::AccountMeta`, `SupplyPositions`, `BorrowPositions`, and `Delegates` are separate persistent keys with independent TTLs, and reads of a missing position map silently default to an empty `Map` instead of failing closed (`get_debt_positions`, `get_supply_positions` at `contracts/controller/src/storage/account.rs:62-73`). If `BorrowPositions(account_id)` archives while `AccountMeta` and `SupplyPositions` stay live, every downstream path sees a debt-free account and the pool's aggregate `borrowed` is orphaned forever.

### Finding Description
Key facts from `contracts/controller/src/storage/account.rs` and `protocol.rs`:

- Each account's data lives under four independent persistent keys (`account.rs:250-256`).
- `get_debt_positions` returns `Map::new(env)` when the key is absent (`account.rs:71-73`); it does not distinguish "no debt" from "key expired".
- Position-map writes deliberately skip TTL renewal: `write_side_map` calls `persistent.set` with no `extend_ttl` (`account.rs:93-105`), while metadata and delegate writes renew via `set_user` (`account.rs:57-60`, `protocol.rs:199-202`). The file header states this asymmetry explicitly: "Metadata and delegate writes renew TTL; position-map writes do not."
- Reads renew only the key actually read (`get_user`, `protocol.rs:190-196`). The only routine renewing all four keys at once is `renew_user_account` (`account.rs:259-272`), invoked from `sync_account_thresholds` and account-touching ops — but paths that only read metadata and supply positions (e.g., `supply`, `update_account_threshold` calls on other accounts, view calls are read-only anyway) leave `BorrowPositions` on its own expiry clock.
- `try_get_account` assembles `Account` from meta + owner + both maps (`account.rs:153-162`); a missing borrow map produces a structurally valid account with `borrow_positions` empty.

Consequently, after `TTL_BUMP_USER` ledgers without a read of the borrow key, `calculate_account_risk_totals` computes `total_debt == 0` → `health_factor = i128::MAX` (per `risk/totals.rs` semantics), so `withdraw` passes its health-factor gate while the real scaled debt is permanently unrecoverable — it exists only in the evicted map; the pool's aggregate `borrowed` state retains it, but no account can ever repay it.

### Impact Explanation
- **Theft of collateral / protocol insolvency**: the account owner withdraws the full collateral (HF gate saturated at `i128::MAX`), while the orphaned aggregate `borrowed` in `PoolStateRaw` makes the corresponding supply claims permanently unbacked. This is equivalent to clean bad debt that no `clean_bad_debt`/`recapitalize` can attribute to an account — the write-down socializes to suppliers.
- **Permanent freezing of unclaimed yield / supplier funds**: the supply side of that market can never be fully redeemed.

### Likelihood Explanation
Requires only that `TTL_BUMP_USER` ledgers elapse without a `BorrowPositions` read — i.e., the user simply avoids `borrow`/`repay`/`liquidate`/`withdraw`/`update_account_threshold` and uses paths that renew only meta + supply keys (e.g., repeated dust `supply`). Soroban archival eviction is deterministic and free for the attacker. Medium likelihood; high impact, consistent with a Medium/High finding.

Uncertainty: I could not confirm within the available iterations whether `supply` (or other always-taken paths) unconditionally loads the borrow map — if every reachable account operation reads `get_debt_positions`, the keys' TTLs would desynchronize far less often, lowering likelihood but not eliminating it (e.g., a pure `supply`-only loop still may not read debt).

### Recommendation
Fail closed on map absence when metadata exists: in `try_get_account`/`get_account`, treat a missing `BorrowPositions` key on an account that ever borrowed as an error, or record a small "has debt" flag inside `AccountMeta` (which is renewed on every write) so a vanished debt map reverts instead of defaulting to empty. Alternatively, make `write_side_map` renew user TTL like `set_user` does, and have any debt-mutating path renew `BorrowPositions`.

### Proof of Concept
1. Attacker supplies XLM collateral in spoke S and borrows USDC; `BorrowPositions(id)` is written with the initial TTL.
2. For `TTL_BUMP_USER` ledgers the attacker performs only `supply` dust deposits (renews `AccountMeta` + `SupplyPositions` via `get_user`) — never reading the borrow key. `BorrowPositions(id)` expires into archival.
3. Attacker calls `withdraw` for the full collateral. `get_account` → `get_debt_positions` returns `Map::new` → `total_debt = 0` → `health_factor = i128::MAX` → gate passes; collateral is paid out.
4. `PoolStateRaw.borrowed` still contains the scaled debt; no account references it → permanent bad debt socialized onto suppliers.