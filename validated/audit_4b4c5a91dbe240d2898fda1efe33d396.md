### Title
Overflow panic in index accrual permanently freezes a market book - (common/src/math/fp_core.rs)

### Summary
The TightVNC null-deref bug class maps onto an untyped arithmetic trap reachable by a single unprivileged caller: `scaled_to_original` performs `Ray::mul` (half-up `x * y / d` in `i128`/`I256`) and panics with `GenericError::MathOverflow` when the product exceeds `i128::MAX`. Because every mutating verb accrues interest first via `global_sync` → `accrue_chunk` → `accrue_step`, once the borrow index × scaled totals crosses the `i128` ceiling the book is bricked: `withdraw`, `repay`, `borrow`, `supply`, `liquidate`, `clean_bad_debt`, `flash_loan`, `recapitalize` and `update_indexes` all revert on the same panic.

### Finding Description
`common/src/math/fp_core.rs:108-143` — `mul_div_half_up` widens `x * y` into `I256` but converts the quotient back via `to_i128`, which panics with `MathOverflow` when the result does not fit (`fp_core.rs:300-303`). `scaled_to_original` calls it directly (`common/src/rates/scaling.rs:14-16`), and accrual computes `borrowed * borrow_index` / `supplied * supply_index` products through it inside `accrue_step` (invoked from `contracts/pool/src/interest.rs:39-53`, which runs on every state-changing call via `global_sync` at `interest.rs:20-33`).

The check that should bound this is the `MAX_BORROW_INDEX_RAY` index cap — but the value ceiling (`i128::MAX ≈ 1.7e38`) is hit *before* the index cap engages for large books. The repo's own harness test proves it: `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:315-360` shows a 1e18-decimals book at ~98% utilization on the XLM rate curve panics in `scaled_to_original` while `borrow_index < MAX_BORROW_INDEX_RAY`, and asserts `try_withdraw_raw` and `try_repay` both fail with `MATH_OVERFLOW`. The comment notes the safe bound documented in `docs/reference/formulas.md` is wrong, so this is not a documented ADR choice.

An attacker seeds the condition unilaterally: list or use an existing high-decimals hub asset, `supply` a very large raw amount (with caps lifted or a high cap, the per-asset `require_cap_within_asset_domain` bound still permits raw totals whose `supplied * index` product exceeds `i128`), then `borrow` to push utilization into the steep rate segment. From then on, time alone drives the index until the next `update_indexes`/`withdraw`/`repay` call — callable by anyone — trips the panic.

### Impact Explanation
Permanent freezing of funds and protocol insolvency. Suppliers cannot withdraw (`unscale_supply` panics through the same multiply), borrowers cannot repay, liquidators cannot liquidate — so underwater positions accrue into bad debt that can never be cleaned or socialized. All token balances held by the pool book for that `(hub, asset)` are permanently locked; the contract holds funds it can never operate on, matching the "permanent freezing of funds" / "contract unable to operate" acceptance criteria.

### Likelihood Explanation
Likelihood is conditional but fully unprivileged: it needs a book whose raw total value approaches ~1e38 ray-units (e.g., ~1e9 whole tokens at 18 decimals, less after index growth) at sustained high utilization on a steep rate curve. A single address can manufacture this against any listed high-decimal asset with a permissive supply cap by supplying and borrowing itself; after that, no further attacker action is required — the freeze is inevitable and triggered by the next public accrual call. It cannot be undone or patched around in-contract because every state path that could reduce the totals itself accrues first.

### Recommendation
- Make accrual overflow-safe: compute the index growth factor separately and multiply `borrow_index`/scaled totals with a saturating or capped path so the `MAX_BORROW_INDEX_RAY` cap engages before the `i128` ceiling; e.g., clamp the index first, then compute `scaled_to_original` only on capped values.
- Alternatively, bound listed markets at listing time (`supply_cap`/decimals validation) so `supplied * MAX_BORROW_INDEX_RAY * RAY` is provably below `i128::MAX`, and enforce it in `require_cap_within_asset_domain`.
- Fix the incorrect bound in `docs/reference/formulas.md` flagged by `large_positions_and_long_horizons.rs:340`.

### Proof of Concept
Reproduced by the existing harness test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:320-360`):

1. Build a book with an 18-decimal asset on the XLM rate curve; lift caps.
2. `supply` 1e9 whole tokens (BOB); Alice supplies collateral and `borrow`s ~98% of the book.
3. Advance time; each year call `update_indexes` (unprivileged).
4. Within ~40 years `try_update_indexes_for` fails with `MATH_OVERFLOW` while `borrow_index < MAX_BORROW_INDEX_RAY`.
5. `try_withdraw_raw(BOB, 1)` and `try_repay(ALICE, 1.0)` both revert with `MATH_OVERFLOW` — the market is permanently frozen: no exit, no repayment, no liquidation, no bad-debt cleanup.