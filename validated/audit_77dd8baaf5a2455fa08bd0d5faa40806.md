### Title
Bad-debt write-down clamps the supply index to a non-zero floor, leaving wiped-out suppliers a phantom claim that drains later repayments and recapitalization cash - ([File: contracts/pool/src/interest.rs](contracts/pool/src/interest.rs))

### Summary
Analogous to the Ajna report (LP shares staying valid after bucket bankruptcy), XOXNO's bad-debt socialization never invalidates existing supply shares. When a cleaned account's debt exceeds the market's total supplied value, `apply_bad_debt_to_supply_index` would drive the supply index to zero, but instead clamps it up to `SUPPLY_INDEX_FLOOR_RAW` (`RAY / 1000`). All pre-existing suppliers keep their full `scaled_amount` shares, now backed by nothing, and the withdraw path only checks `require_reserves` (cash ≥ payout) — not backing. Any later cash inflow (repayment of other borrowers' surviving debt, or permissionless `recapitalize`) can be withdrawn by these phantom claims first-come-first-served, stealing funds owed to honest suppliers and recapitalizers.

### Finding Description
`clean_bad_debt` (permissionless, `contracts/controller/src/lib.rs:163`) routes to pool seize, which calls `interest::apply_bad_debt_to_supply_index` for each borrow leg and burns the debt (`contracts/pool/src/ops/seize.rs:24-28`). The write-down computes `new_supply_index = floor(old_index * (total_value - min(bad_debt, total_value)) / total_value)` and then applies `.max(Ray::from(SUPPLY_INDEX_FLOOR_RAW))` (`contracts/pool/src/interest.rs:73-88`). When `bad_debt >= total_supplied_value` (a total wipeout), the index is clamped *up* to `10^24` instead of zero, so every supplier retains `scaled_amount × 10^24` of claim value while the market holds no backing for it — the docs acknowledge this: "The non-zero floor can leave residual claims without backing" (`docs/reference/formulas.md:399`).

The exit path enforces only `cache.require_reserves(net_transfer)`, `require_utilization_below_max`, and `require_supply_for_debt` before `debit_cash` (`contracts/pool/src/ops/withdraw.rs:111-118`). None of these compare claims to `cash + debt` backing — that check (`INV-ACCT-04`) only gates *new supply*. So a wiped-out supplier can call controller `withdraw` the moment the market's tracked cash covers their floor-valued claim. Cash arrives through other borrowers' repayments (their debt shares are untouched — only the cleaned account's debt is burned, `seize.rs:27`) or through permissionless `recapitalize`, which fills exactly the measured shortfall without minting shares.

The same mechanism is already demonstrated at the cache level by the project's own test `test_raw_cache_floor_clamp_strands_claim_without_supply_guard` (`contracts/pool/tests/interest.rs:372-428`), which shows the stranded position paying out real tokens and leaving an honest claim unbacked. The test relies on direct `mint_supply`/`credit_cash` for the fresh deposit, but the identical drain works through the production `repay` → `withdraw` path, which is reachable by any unprivileged address.

### Impact Explanation
Theft of user funds / permanent loss: after a wipeout write-down, holders of economically worthless supply shares withdraw real tokens that belong to surviving suppliers' claims or to whoever recapitalized the market. Whoever withdraws last (or a recapitalizer filling the shortfall) absorbs the loss. The loss equals up to `supplied × floor_index` of claim value against every unit of cash that subsequently enters the market.

### Likelihood Explanation
Reachable entirely by unprivileged addresses: `clean_bad_debt(caller, account_id)` needs only `ceil_risk_debt > half_up_collateral` and collateral ≤ $5, attainable after a price crash; the cleaned account's debt must exceed the market's total supplied value to trigger the floor clamp. Afterwards the attacker simply calls `withdraw` when repayments of remaining borrowers (or a recapitalizer) restore cash. No timing or privilege is required; the claim persists indefinitely because shares are never invalidated — exactly the bug class of the source report.

### Recommendation
- On a wipeout write-down, allow the supply index to reach zero (or burn/void supply shares pro-rata to actual remaining backing) instead of clamping to `SUPPLY_INDEX_FLOOR_RAW`, so no unbacked claim survives.
- Alternatively, gate `withdraw` (and revenue claims) on the same backing check used for supply — pay each claim only its pro-rata share of `cash + debt_value` rather than raw `require_reserves`.
- Track a per-market "bankrupt" watermark analogous to Ajna's `bankruptcyTime` and zero out claims that predate a total wipeout.

### Proof of Concept
1. Market M has suppliers totaling `S` shares, index `RAY`, cash fully lent; borrower A holds debt `D ≥ value(S)` plus borrower B holds small surviving debt.
2. Price crash makes A's account insolvent with ≤$5 collateral. Anyone calls `controller.clean_bad_debt(caller, A_id)`.
3. `apply_bad_debt_to_supply_index` computes `remaining = 0`, `reduction_factor = 0`, then clamps: `supply_index = max(0, RAY/1000) = 10^24`. A's debt shares burn; B's debt survives.
4. A supplier holding `s` shares now has a floor-valued claim `floor(s × 10^24 / unit)` with zero backing.
5. B repays (or a third party calls `recapitalize`), crediting cash. The wiped supplier calls `controller.withdraw`; `require_reserves` passes and the phantom claim pays out real tokens.
6. Honest suppliers' residual claims and/or the recapitalizer end up unbacked — confirmed by the existing unit test at `contracts/pool/tests/interest.rs:414-426` showing a stranded position draining cash so a fresh claim can no longer be covered.