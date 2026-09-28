### Title
Sub-3-decimal collateral can enter an unliquidatable repayment band - (File: contracts/controller/src/positions/liquidation/math.rs)

### Summary
A solvent but unhealthy account whose only collateral uses fewer than `MIN_BORROWABLE_ASSET_DECIMALS` decimals can reach a state where every `liquidate` call reverts. The liquidation planner refuses both available whole-unit adjustments, the pro-rata seizure rounds to zero collateral units, the planner then releases the now-unbacked repayment, and the resulting empty repayment plan is rejected.

### Finding Description
`whole_unit_repayment` special-cases an account with exactly one supply position and a collateral decimal count below `MIN_BORROWABLE_ASSET_DECIMALS`. It preserves the original quote when:

1. the quote-backed seizure is below one collateral unit;
2. one unit divided by `1 + bonus` does not cover total debt plus one unit of each debt leg; and
3. the raised one-unit repayment is at least the total debt.

Those conditions are checked in `contracts/controller/src/positions/liquidation/math.rs:226-290`.

Later, `calculate_seized_collateral` rounds a partial low-decimal collateral seizure down to whole units. When the quote backs less than one unit, that seizure becomes zero. `build_liquidation_plan` releases the repayment that is no longer backed by seized collateral; with no other collateral legs, `seized_collaterals` is empty and the entire repayment is released. `process_liquidation` then rejects the empty `result.repaid` vector with `InvalidPayments` at `contracts/controller/src/positions/liquidation/mod.rs:58-67`.

Both `SeizeMode::Transfer` and `SeizeMode::Credit` traverse the same plan, so selecting share-credit mode does not avoid the empty-seizure failure.

### Impact Explanation
While the account remains in this band, liquidation cannot recover lender funds or remove risk from the pool. The borrower also cannot withdraw the collateral because the account is unhealthy. If the account remains solvent, permissionless `clean_bad_debt` cannot process it because debt does not exceed collateral. Recovery remains unavailable until accrual, a price change, repayment, or another transaction moves the account out of the band, causing temporary freezing of collateral and delayed recovery of borrowed pool funds.

### Likelihood Explanation
An unprivileged borrower can create the required shape using only `supply` and `borrow`: open an account with exactly one listed collateral position using a sub-3-decimal asset, borrow an allowed debt asset, and let interest or price movement reduce health factor below one while debt remains inside the gap. No privileged action or malformed external contract is required. The affected state is temporary rather than permanent, and it depends on a listed low-decimal collateral market and suitable price/debt parameters.

### Recommendation
Handle the one-unit boundary explicitly instead of preserving a quote that necessarily rounds to zero. For example, promote the plan to a bounded whole-unit/full-close plan when one indivisible collateral unit is available, recalculate the effective bonus for that close, or keep a fractional share-based `Credit` seizure representation that cannot collapse to zero. Add regression coverage for all `SeizeMode` variants in the band where `unit_at_bonus < total_debt + debt_units` but `unit_repayment >= total_debt`.

### Proof of Concept
Assume a configured market has:

- one 0-decimal collateral token worth `$1,000` per unit;
- liquidation threshold `70%`;
- base liquidation bonus `5%`;
- one 7-decimal stablecoin debt asset worth `$1`;
- the target health factor used by the curve is `1.10`.

1. An attacker calls:

   ```text
   supply(
       caller = attacker,
       account_id = 0,
       spoke_id = S,
       assets = [(HubAssetKey { hub_id: H, asset: LOW_DECIMAL }, 1)]
   )
   ```

   This creates account `A` with one collateral unit.

2. The attacker calls:

   ```text
   borrow(
       caller = attacker,
       account_id = A,
       borrows = [(USDC_KEY, 600_0000000)],
       to = None
   )
   ```

3. Interest accrues until debt is `$900`. The account is unhealthy:

   ```text
   weighted collateral = $1,000 * 70% = $700
   health factor       = $700 / $900 = 0.777...
   ```

4. The normal liquidation quote is approximately:

   ```text
   (($900 * 1.10) - $700) / (1.10 - (0.70 * 1.05))
       = $794.52
   ```

   Its bonus-backed seizure is approximately `$834.25`, below one `$1,000` collateral unit.

5. `whole_unit_repayment` does not correct the quote:

   ```text
   unit / (1 + bonus)
       = $952.38
       < $900 + one-debt-unit margin

   unit_with_margin / (1 + bonus)
       > $900
   ```

6. Any liquidator call such as:

   ```text
   liquidate(
       liquidator = liquidator,
       account_id = A,
       debt_payments = [(USDC_KEY, 900_0000000)],
       seize_mode = SeizeMode::Transfer
   )
   ```

   is normalized toward the approximately `$794.52` quote, the collateral seizure rounds down to zero units, the repayment is released as unbacked, and the empty repayment plan reverts. Using `SeizeMode::Credit(0)` follows the same seizure calculation and also reverts. The account remains unliquidatable until debt, price, or another state change exits the band.