### Title
Accrual-time i128 overflow in `scaled_to_original` permanently freezes a market — no repay, withdraw, or liquidation can execute — ([File: common/src/rates/simulate.rs])

### Summary
Every controller verb touching a market (`borrow`, `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `recapitalize`, and the permissionless `update_indexes`) runs interest accrual first. The accrual step unscale multiplies `borrowed * borrow_index` and `supplied * supply_index` in `i128` via a *panicking* half-up multiply-divide. Once a market's RAY-valued book grows past `i128::MAX` — reachable below the 10^36 index ceiling whenever the market holds very large balances at sustained high utilization — the next accrual panics with `MathOverflow`, and every subsequent call on that market panics forever. All user deposits in that market are permanently frozen and all outstanding debt becomes permanently unrepayable/unliquidatable, with no admin escape hatch on these paths.

### Finding Description
`accrue_step` (`common/src/rates/simulate.rs:60-61`) calls `scaled_to_original`, which is `scaled.mul(env, index)` — a half-up `x * y / RAY` that widens to `I256` for the intermediate but panics with `GenericError::MathOverflow` if the *result* does not fit `i128` (`common/src/math/fp_core.rs:148-159`, `common/src/rates/scaling.rs:14-16`). The mutating path `global_sync` → `accrue_chunk` runs this unconditionally for any nonzero elapsed time (`contracts/pool/src/interest.rs:20-53`).

Two critical properties make this a trap rather than a transient revert:

1. **Accrual is a mandatory prefix.** Withdraw, repay, liquidation, and bad-debt cleanup all accrue the market before touching balances, so a panicking accrual bricks *exit* paths, not just entry — the rejected "fail-closed revert" pattern does not apply because there is no non-accruing alternative path.
2. **The borrow-index cap does not prevent it.** `update_borrow_index` clamps *after* multiplying (`common/src/rates/index.rs`; tested at `common/tests/rates/index.rs:497-518`), and the value overflow in `scaled_to_original`/`calculate_supplier_rewards` triggers before the index ever reaches `MAX_BORROW_INDEX_RAY` — proven by the in-repo test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-360`), which asserts `MATH_OVERFLOW` on `update_indexes`, `withdraw`, and `repay`, with `borrow_index < MAX_BORROW_INDEX_RAY`.

The docs acknowledge the cliff (`docs/reference/formulas.md:432-437`: "Value overflow can occur before the index ceiling and block repayment/withdrawal"), and `docs/reference/invariants.md` INV-IDX-01 states "Debt-value overflow can still revert accrual before that ceiling is reached." So the arithmetic ceiling is documented — but there is no mitigation path: no governance rescue, no non-accruing exit, no satura­ting accrual. Once crossed, `recapitalize` also accrues first and cannot help.

The reachable trigger is unprivileged: any address may open maximal positions within listed caps (caps admit up to ~170 billion whole tokens, `formulas.md:429`) and then call `update_indexes(caller, assets)` — an explicitly permissionless, "gated" (unpaused) endpoint (`docs/reference/endpoints.md:37`) — after sufficient time accrues. At ~98–100% utilization on a steep rate curve, the scaled debt value crosses `i128::MAX` within a bounded number of accrual chunks (the test reaches it in tens of simulated years at the XLM curve; markets listed with higher caps/decimals compress the boundary). Notably, an attacker does not need to wait for their own position to overflow: any whale market legitimately near the value ceiling can be pushed over by the attacker's `update_indexes` call arriving with a large `delta_ms`, and the panic persists because `last_timestamp` only advances on success.

### Impact Explanation
Permanent freezing of user funds and protocol insolvency in the affected (hub, token) market. Suppliers cannot withdraw (accrual panics first), borrowers cannot repay, liquidators cannot liquidate (so the account's collateral in *other* markets is also stranded behind the frozen debt leg until governance intervention), and `clean_bad_debt`/`recapitalize` accrue first too, so even the bad-debt recovery path is dead. This satisfies the "permanent freezing of funds" acceptance class directly.

### Likelihood Explanation
Requires a market whose RAY book approaches `i128::MAX` (~1.7e38 raw RAY value, i.e., ~1.7e11 whole-token equivalents at index 1, scaled by index growth). That is a large but *admitted* domain: caps up to ~170 billion whole tokens are valid listings, and sustained high utilization at up to 200% APR compounds the borrow index up to 10^9× before its cap. The trigger needs no privilege — `update_indexes` is public — and no price manipulation, only time and an already-large market. Realistic likelihood is low-to-moderate; impact is maximal. Severity: Medium (High impact gated by the market-size precondition).

### Recommendation
Make the value unscale in `accrue_step` saturating instead of panicking (e.g., `mul_div_floor_saturating` for `borrowed_original`/`supplied_original`, mirroring the deliberate fail-open choice in `calculate_scaled_cap`, `common/src/rates/scaling.rs:26-33`), or clamp the borrow index *before* the `borrowed × index` product so accrual degrades to "no further interest" rather than trapping. Alternatively, add an emergency non-accruing exit path (e.g., allow `withdraw`/`clean_bad_debt` to skip accrual when the stored book is provably past the representable bound), so the overflow cliff degrades into frozen interest rather than frozen principal.

### Proof of Concept
Already exercised in-repo:

```rust
// tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-356
t.supply_raw(BOB, "BIG18", principal);          // 1e9 * 10^18 units
t.borrow_raw(ALICE, "BIG18", debt);             // ~98% utilization
loop { t.advance_time(YEAR_SECS);
       if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; } }
// => MathOverflow while borrow_index < MAX_BORROW_INDEX_RAY
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

An unprivileged attacker path: (1) `supply`/`borrow` a market up to its admitted caps at high utilization (or wait for organic growth), (2) call `update_indexes(caller, [hub_asset])` once enough `delta_ms` has elapsed — the call reverts with `MathOverflow`, and every later call on that market reverts identically because `last_timestamp` never advances.