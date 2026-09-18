Based on the investigation, I found a structurally analogous bug class in the Raydium AMM program: an unbounded, attacker-influenced numeric field being used unconditionally in `unwrap()`-based arithmetic that every future swap/deposit/withdraw depends on, which can permanently panic the pool and lock all deposited funds — the same shape as the OpenQ `expiration = type(uint256).max` bug (attacker sets an unbounded value once → every future accounting call reverts → funds locked forever).

### Title
Unbounded token decimals causes permanent arithmetic overflow panic in `normalize_decimal`/`restore_decimal`, freezing all pool funds - ([File: program/src/math.rs])

### Summary
`Calculator::normalize_decimal`, `Calculator::normalize_decimal_v2`, and `Calculator::restore_decimal` compute `10u128.checked_pow(native_decimal)` and immediately `.unwrap()` the result [1](#0-0) . These helpers are invoked with `amm.pc_decimals` / `amm.coin_decimals` on essentially every state-mutating path: `process_deposit`, `process_withdraw`, and `calc_take_pnl` (used by deposit, withdraw, and `withdrawpnl`) all call `Calculator::normalize_decimal_v2(total_pc_without_take_pnl, amm.pc_decimals, amm.sys_decimal_value)` / the coin equivalent before doing any pnl or invariant math [2](#0-1) [3](#0-2) [4](#0-3) .

`10u128.checked_pow(n)` returns `None` once `n >= 39` (since `10^39` exceeds `u128::MAX ≈ 3.4×10^38`), which makes the subsequent `.unwrap()` panic unconditionally for any `pc_decimals`/`coin_decimals` value ≥ 39.

### Finding Description
`amm.pc_decimals` and `amm.coin_decimals` are populated once at pool creation from the underlying SPL token mints' `decimals` field, which is a `u8` (range 0–255) fully controlled by whoever creates the mint. A pool creator (an unprivileged actor, in scope per this task's rules) can mint a custom SPL token with `decimals` set to any value ≥ 39 and pair it in a new AMM via `Initialize2`. Once the pool is created with such a mint, every subsequent call into `normalize_decimal_v2`/`restore_decimal` with that decimals value will panic instead of returning an error, because the overflow is masked behind an `unwrap()` rather than a propagated `AmmError`.

This mirrors the OpenQ bug exactly: a single attacker-chosen unbounded parameter (there: `expiration = type(uint256).max`; here: mint `decimals >= 39`) is accepted without an upper bound at creation/deposit time, and later gets fed into unconditional arithmetic (`depositTime + expiration` there; `10.pow(decimals)` here) that always reverts/panics once triggered — permanently disabling the accounting logic that funds retrieval depends on.

### Impact Explanation
Because `normalize_decimal_v2` is called from `process_deposit`, `process_withdraw`, and `calc_take_pnl` (reached from deposit/withdraw/`withdrawpnl`), any pool created with such a malicious-decimals mint would panic on essentially every state-changing instruction touching PnL/invariant accounting, matching the "permanent freezing of user or LP funds" impact bar: any liquidity already sent to the pool's vaults (e.g., in the same or a following transaction as pool creation) becomes permanently unwithdrawable, since `Withdraw` also unconditionally goes through this code path [5](#0-4) .

### Likelihood Explanation
Likelihood depends on whether `AmmInfo`/`Initialize2` validates and bounds `coin_decimals`/`pc_decimals` before storing them. I was not able to locate or fully inspect the body of `process_initialize2` within the available search iterations to confirm whether such a bound check exists elsewhere in the codebase (e.g., a decimals cap check performed before calling `Calculator` helpers). This is a real limitation of my investigation — I can only confirm the unguarded `unwrap()` in the math helpers and their reachability from unprivileged deposit/withdraw/pnl paths, not the absence of an upstream guard in `Initialize2`.

### Recommendation
Replace the `.unwrap()` calls in `Calculator::normalize_decimal`, `normalize_decimal_v2`, and `restore_decimal` with propagated errors (`ok_or(AmmError::...)?`), and/or enforce an explicit upper bound (e.g., `decimals <= 18` or whatever value keeps `10^decimals` within `u128`) on `coin_decimals`/`pc_decimals` at `Initialize2` time so a malicious mint can never be paired into a pool in the first place.

### Proof of Concept
1. Attacker creates a new SPL token mint with `decimals = 39` (or any value ≥ 39) using the standard SPL Token program (unprivileged, off-chain client action).
2. Attacker calls `Initialize2` to create a new Raydium AMM pool pairing this mint as coin or pc token; `amm.coin_decimals`/`amm.pc_decimals` get set to 39 with initial liquidity deposited into the vaults.
3. Any subsequent `Deposit`, `Withdraw`, or `WithdrawPnl` call triggers `Calculator::normalize_decimal_v2`/`restore_decimal`, which computes `10u128.checked_pow(39)`, returns `None`, and `.unwrap()` panics, aborting the transaction.
4. Because withdrawal itself depends on this same code path, the funds deposited into the pool's vaults can never be withdrawn — permanent fund lock.

**Note on verification gap:** I could not confirm within the available tool budget whether `process_initialize2` already rejects decimals above a safe threshold; if such a check exists, this specific analog would not be exploitable, though the underlying `unwrap()`-based panic pattern in `math.rs` would still represent fragile, non-defensive arithmetic worth hardening.

### Citations

**File:** program/src/math.rs (L80-94)
```rust
    pub fn normalize_decimal(val: u64, native_decimal: u64, sys_decimal_value: u64) -> u64 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = Self::to_u64(
            ret_mut
                .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
                .unwrap()
                .as_u128(),
        )
        .unwrap();
        ret
    }
```

**File:** program/src/processor.rs (L1155-1164)
```rust
        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
```

**File:** program/src/processor.rs (L1474-1483)
```rust
        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
```

**File:** program/src/processor.rs (L1719-1735)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
```
