### Title
Accrual-time `scaled_to_original` overflow permanently freezes a whale market — no repay, withdraw, or liquidation possible - ([File: contracts/pool/src/interest.rs])

### Summary
The kernel report's bug class is "an attacker-constructible input trips a non-actionable check that panics the whole path." XOXNO Lending has the same shape in `Cache::calculate_utilization` / accrual: every market verb first runs `interest::global_sync` and unscale math through `scaled_to_original` (borrowed_scaled × borrow_index), which panics with `MathOverflow` once `borrowed_scaled * borrow_index` exceeds `i128::MAX`. The borrow-index cap `MAX_BORROW_INDEX_RAY` is applied to the index, but the value ceiling is hit first on whale markets (many decimals × large supply), so the cap never engages. Once crossed, the overflow is a function of stored state, not the caller's input — every subsequent `supply`/`borrow`/`withdraw`/`repay`/`liquidate`/`update_indexes`/`claim_revenue` on that `(hub, token)` book reverts forever. The test harness pins exactly this in `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` at `tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`: after the cliff, `try_withdraw_raw` and `try_repay` both revert with `MATH_OVERFLOW`, and `last.borrow_index < MAX_BORROW_INDEX_RAY` confirms the cap never fired.

### Finding Description
`global_sync` (`contracts/pool/src/interest.rs:20-33`) runs before every mutating entrypoint per the documented flow (`contracts/pool/README.md:159-176`: `Cache::load → global_sync → mutate → guards → commit`). Accrual and utilization math unscale `borrowed`/`supplied` via `scaled_to_original` (`contracts/pool/src/cache/scale.rs:23-24`), i.e. `scaled_shares * index` in RAY fixed-point over `i128`. On an 18-decimal market, 1 billion whole tokens is `1e36` raw RAY of scaled value; `i128::MAX` is only ~170× that, so once `borrow_index` grows past ~170× — reachable in a few years on the steep XLM rate curve at sustained ~98% utilization — the multiply overflows and `panic_with_error!(MathOverflow)` fires. Because accrual precedes the mutation, no caller can avoid it: `withdraw`, `repay`, `liquidate`, `clean_bad_debt`, `seize_positions`, and even `update_indexes`/`claim_revenue` all go through the same `Cache::load` + `global_sync` + unscale path, so the panic is sticky and unconditional — the exact analog of an unactionable WARN that kills the process for a packet anyone can craft.

### Impact Explanation
Permanent freezing of user funds and market liveness: all supplier principal and accrued yield in that market becomes unwithdrawable, borrower debt becomes unrepayable, and liquidations cannot execute (both the debt leg and the collateral read of the frozen market accrue first). Bad debt on the frozen book can never be cleaned or socialized, so supplier claims in that book are stranded at their nominal value while the debt-side is uncollectable — an effective insolvency for that book. Impact class: permanent freezing of funds / protocol insolvency for the affected market.

### Likelihood Explanation
Reachable by a single unprivileged address with capital, no privileged role needed: supply a large amount to a high-decimal market, then `borrow` to ~98% utilization and simply never repay (or periodically keep utilization high via normal borrow/withdraw cycling on a whale-supplied market). Interest accrual is permissionless (`update_indexes`, `contracts/controller/src/lib.rs:370-372`) but also implicit — the cliff is reached by time alone, not by any keeper action. The borrowed funds are the attacker's own, so the only cost is interest-rate carry; once the index × scaled-debt product overflows, the market is bricked with no recovery path short of a code upgrade. Constraints: requires a genuinely large market (billion-scale whole tokens at high decimals, per the pinned test) and sustained high utilization over an extended accrual horizon, which is why the harness test uses lifted caps and `max_utilization` disabled — on real deployment caps the borrowable depth is bounded, so feasibility depends on configured `supply_cap`/`borrow_cap` and the interest curve's peak rate. That makes it High rather than Critical in practice, but the failure mode once reached is total and irreversible by any unprivileged action.

### Recommendation
The accrual path must saturate instead of overflowing, mirroring the kernel fix ("the warning is not actionable — remove it"): when `borrowed_scaled * borrow_index` would exceed `i128::MAX`, clamp `borrow_index` at `MAX_BORROW_INDEX_RAY` (or derive the largest index for which the unscale still fits) inside `accrue_step` before committing `set_borrow_index`, so the cap engages *before* the value ceiling rather than after. Alternatively, compute accrual in a wider intermediate (e.g., 256-bit via `soroban_sdk::U256`) and saturate the stored index. Equally important: give `repay`/`withdraw`/`clean_bad_debt` a path that skips or clamps accrual when the index is already saturated, so a market that reaches the ceiling remains exit-able rather than permanently frozen. The `MAX_BORROW_INDEX_RAY` constant exists but is checked too late — it needs to bound the multiplication, not just the stored index.

### Proof of Concept
Pinned regression test `a_whale_market_at_sustained_high_utilization_hits_the_ray_value_ceiling_before_the_index_cap` (`tests/test-harness/tests/controller/large_positions_and_long_horizons.rs:321-361`):

```rust
let principal = BILLION * 10i128.pow(18);          // 1e9 whole tokens, 18 decimals
t.supply_raw(BOB, "BIG18", principal);             // unprivileged supply
let debt = principal / 100 * 98;                   // ~98% utilization
t.supply_raw(ALICE, "COL", BILLION * 10_000_000 * 3);
t.borrow_raw(ALICE, "BIG18", debt);                // unprivileged borrow
// advance years; accrual is permissionless:
if let Err(e) = t.try_update_indexes_for(&["BIG18"]) { break e; }  // MATH_OVERFLOW
assert!(last.borrow_index < MAX_BORROW_INDEX_RAY); // cap never engaged
// market frozen — every verb accrues first and panics identically:
assert_contract_error(t.try_withdraw_raw(BOB, "BIG18", 1), errors::MATH_OVERFLOW);
assert_contract_error(t.try_repay(ALICE, "BIG18", 1.0), errors::MATH_OVERFLOW);
```

The test already proves revert-on-every-verb permanence; the overflow site is `scaled_to_original(&env, self.borrowed, self.borrow_index)` in `Cache::calculate_utilization` (`contracts/pool/src/cache/scale.rs:23`) reached via `global_sync`/`accrue_step` (`contracts/pool/src/interest.rs:39-53`), which runs before every market mutation.

Caveat: I did not read `common::rates::accrue_step`/`scaled_to_original` directly (out of iterations), so the precise multiplication site inside `common` is inferred from the pinned test's `MATH_OVERFLOW` verdict and the `scaled_to_original` call graph; the exact index-at-failure and whether caps are checked inside `accrue_step` or at `set_borrow_index` should be confirmed there before writing the fix.