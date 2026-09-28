### Title
Permissionless `clean_bad_debt` pays the caller nothing, so dust bad-debt accounts stay unsocialized and supplier withdrawals freeze - (File: contracts/controller/src/positions/liquidation/bad_debt.rs)

### Summary
Analogous to M-1 (MultiInvoker pays keepers no calldata refund, so keepers are not incentivized to execute), XOXNO Lending relies on a permissionless keeper call — `clean_bad_debt` — to socialize insolvent dust accounts, but compensates the caller with nothing. All remaining collateral is reclassified to protocol revenue and all residual debt is written down against suppliers; the caller only bears the transaction cost. Until someone volunteers, the dead debt stays on the market books, the backing shortfall blocks supply-side operations, and cash exhaustion freezes supplier withdrawals.

### Finding Description
`Controller::clean_bad_debt` is explicitly permissionless: `contracts/controller/src/lib.rs:163` calls `positions::liquidation::process_clean_bad_debt`, which only does `caller.require_auth()` plus a flash-loan guard before `clean_bad_debt_standalone` (`contracts/controller/src/positions/liquidation/mod.rs:196-200`). The gate `is_socializable_bad_debt` requires `total_debt > total_collateral` and collateral at or below the fixed $5 `BAD_DEBT_USD_THRESHOLD` (`contracts/controller/src/positions/liquidation/mod.rs:229-235`; `skills/xoxno-lending/math.md:417`).

`execute_bad_debt_cleanup` (`contracts/controller/src/positions/liquidation/bad_debt.rs:14-61`) then seizes every supply leg into revenue and burns every debt leg via `pool_seize_positions_call`, releases spoke usage, emits `CleanBadDebtEvent`, and deletes the account/NFT. There is no branch that credits the `caller` — unlike `liquidate`, which pays a collateral bonus (`contracts/controller/src/positions/liquidation/math.rs:482-501`), cleanup transfers zero value to the keeper.

The consequences of debt never being cleaned are concrete:

- While the phantom debt remains, `borrowed` is inflated, so `require_utilization_below_max` (`contracts/pool/src/guards.rs:19-34`) and `require_backed_market`/`backing_shortfall` (`contracts/pool/src/guards.rs:52-66`) treat the market as over-utilized or short of backing, gating operations that check it.
- Suppliers holding claims against a market whose cash was fully lent into this account cannot withdraw: once `cash < claim`, exits fail, so supplier funds are frozen until a charitable caller socializes the debt and the supply index is written down (`docs/reference/formulas.md:386-401`).
- The alternative `force_socialize_bad_debt` is owner-gated with a timelock (`docs/reference/runbooks/force-socialize-bad-debt.md:43-46`), so the permissionless path is the only timely unprivileged route.

### Impact Explanation
Temporary freezing of user funds: bad debt sitting above the $5-less collateral forces `backing_shortfall > 0` only after write-down, but pre-cleanup the unrecoverable debt still counts as backing while consuming no cash — suppliers attempting `withdraw` hit insufficient cash, and `recapitalize`/`PoolInsolvent` gates keep the market impaired. This persists indefinitely absent an altruistic keeper, exactly the "keeper not incentivized" impact class of M-1. Severity Medium: funds are not stolen, but availability depends on unpaid third parties or slow governance.

### Likelihood Explanation
Any unprivileged user can create the precondition: open an account, supply a small amount, borrow, then a price move (or accrued interest on `update_indexes`, also permissionless) pushes `D > C` with `C <= $5`. Such dust bad-debt accounts arise naturally from partial liquidations too — the docs note residual debt below $5 can remain (`docs/reference/formulas.md:327-339`). Since cleanup costs the caller a Soroban fee and returns nothing, rational keepers skip it; the bundled keeper service is optional infrastructure (`services/keeper/README.md`), not an on-chain guarantee.

### Recommendation
Pay the cleanup caller a small reward in `execute_bad_debt_cleanup` — e.g., transfer a fixed amount or a fraction of the seized collateral revenue before reclassifying it (the pool already supports revenue/share reclassification and transfers, as used by `SeizeMode::Transfer` in `contracts/controller/src/positions/liquidation/math.rs:482-501`). Alternatively, allow `clean_bad_debt` callers to receive a claim on the written-down collateral legs similar to the liquidation bonus path, sized to exceed typical Soroban execution cost.

### Proof of Concept
1. `supply` ~$10 of COL, `borrow` ~$9 of DEBT.
2. Drop COL price so `total_debt > total_collateral` and `total_collateral <= 5 WAD` (the gate opens; `tests/test-harness/tests/controller/dust_threshold_and_decimal_floor.rs:165-214` demonstrates a price sweep reaching exactly this state).
3. Any third party calls `clean_bad_debt(caller, account_id)`. On success, `execute_bad_debt_cleanup` pushes all of the account's supply shares to revenue and burns the debt (`bad_debt.rs:22-49`); the caller's token balances are unchanged (compare with the liquidation flow in `tests/test-harness/tests/controller/liquidation_extreme.rs:689-715`, where the liquidator's balance increases by `seized - fee`).
4. Before step 3 runs, suppliers of the debt market attempting `withdraw` for more than `cash` fail, since the dead debt inflates `borrowed`/`backing` while providing no liquidity (`guards.rs:39-66`).