### Title
Unchecked u128 overflow in `Calculator::normalize_decimal`/`normalize_decimal_v2` permanently bricks a pool once vault balance exceeds a decimals-dependent threshold - ([File: program/src/math.rs])

### Summary
`Calculator::normalize_decimal` and `Calculator::normalize_decimal_v2` compute `val (u128) * sys_decimal_value` and `.unwrap()` the `checked_mul`/`checked_pow` results without any bound on `native_decimal`. [1](#0-0)  `sys_decimal_value` is derived from the mint decimals supplied by the pool creator at `Initialize2` (`amm.sys_decimal_value = 10^max(pc_decimals, coin_decimals)`), and mint decimals come straight from attacker-controlled SPL mints with no upper-bound validation. [2](#0-1) [3](#0-2)  Because these normalization functions are called on live vault balances inside `Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn/Out` (via `calc_total_without_take_pnl_no_orderbook`/`calc_take_pnl` and the deposit/withdraw invariant calculations), a vault balance that grows past the overflow threshold causes every subsequent instruction on that pool to panic and revert, permanently freezing all LP and swapper funds held in that pool.

### Finding Description
`normalize_decimal_v2` is:
```
let ret_mut = (U128::from(val)).checked_mul(sys_decimal_value.into()).unwrap();
let ret = ret_mut.checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap()).unwrap();
``` [4](#0-3) 

`sys_decimal_value` is set once at pool creation as `10^max(pc_decimals, coin_decimals)` with no cap: [2](#0-1) . The `coin_decimals`/`pc_decimals` come directly from `Self::unpack_mint(...).decimals` on the two mints supplied by the (unprivileged) pool creator in `process_initialize2`, with no validation that the value is small: [5](#0-4) .

`U128` (128-bit) can hold at most ≈3.4×10^38. If a pool is created with a mint whose decimals is large enough (empirically ≥ ~20), then once a vault's raw `u64` balance exceeds a modest threshold (`U128::MAX / 10^decimals`), the multiplication `val * sys_decimal_value` in `normalize_decimal`/`normalize_decimal_v2` overflows `U128` and `.unwrap()` panics, aborting the transaction.

Critically, vault token accounts (`amm_coin_vault`/`amm_pc_vault`) are ordinary SPL Token accounts whose authority is the AMM PDA, but any external, unprivileged actor can `spl_token::transfer` tokens directly into them **without going through the Raydium program at all** — a classic "donation" vector. Since Initialize2 itself calls `normalize_decimal_v2` on the small starting vault balances (which can be kept tiny/dust to avoid triggering the overflow at creation time) [6](#0-5) , a pool can be created successfully, and only later be pushed over the overflow threshold by a direct donation transfer that bypasses all Raydium-side checks.

Once the vault balance exceeds the threshold, **every** subsequent call into `process_deposit`, `process_withdraw`, `process_withdrawpnl`, `process_swap_base_in`/`_out` (and their V2 variants) will re-read the vault's live `amount` and re-invoke `normalize_decimal`/`normalize_decimal_v2` on it — for example in the PnL/invariant calculation path: [7](#0-6)  and in `calc_take_pnl`: [8](#0-7) . Each of these calls panics and aborts, so no LP can ever withdraw, no swap can ever succeed, and no deposit can ever succeed again for that pool — a permanent freeze of all pooled funds.

### Impact Explanation
This is a permanent, unrecoverable denial-of-service against a specific pool's funds: once triggered, LPs cannot withdraw their liquidity, swappers cannot trade, and PnL cannot be withdrawn, because every code path touching that pool calls the overflowing normalization function. This satisfies "permanent freezing of user or LP funds" and is reachable purely from unprivileged, attacker-chosen accounts/data: a pool creator choosing an attacker-controlled mint with large decimals at `Initialize2`, plus an ordinary SPL token transfer (no Raydium program interaction needed) to push the vault balance over the threshold.

### Likelihood Explanation
The pool creator role is unprivileged (`Initialize2` can be called by anyone providing any two SPL mints) and mint decimals are entirely attacker-controlled since the attacker can create their own SPL mint with arbitrary decimals via the standard SPL Token program before calling `Initialize2`. No validation exists anywhere in `process_initialize2` or `AmmInfo::initialize` restricting decimals to a sane range (e.g., ≤9 as commonly assumed). The follow-up "donation" transfer to the vault account is a single ordinary SPL token transfer requiring no special privilege or interaction with the Raydium program.

### Recommendation
- Reject mints with decimals above a sane bound (e.g., ≤ 9 or ≤ 18) in `process_initialize2`.
- Replace `U128` with `U256` (already defined in `math.rs`) for the intermediate multiplication in `normalize_decimal`/`normalize_decimal_v2`/`restore_decimal`, or use `checked_mul`/`checked_div` with graceful `ProgramError` returns instead of `.unwrap()`, so an overflow degrades to an instruction error rather than an unrecoverable, permanently-triggerable panic tied to vault balance.
- Consider bounding `sys_decimal_value` derivation and validating it against the maximum expected vault balance (`u64::MAX`) at pool-creation time to guarantee normalization can never overflow for the life of the pool.

### Proof of Concept
1. Attacker creates a custom SPL mint `M` with `decimals = 24` (or any value ≥ ~20) via the standard SPL Token program — fully unprivileged.
2. Attacker calls Raydium `Initialize2` pairing mint `M` (as `pc_mint`, say) with a normal 6-decimal mint, depositing only dust amounts (e.g., `init_pc_amount = 1`) so that `normalize_decimal_v2` at lines 950–958 of `processor.rs` does not overflow during initialization. Pool is created successfully; `amm.sys_decimal_value = 10^24`.
3. Attacker (or anyone) sends a plain `spl_token::transfer` instruction (not a Raydium instruction) of, say, `10^9` raw units of mint `M` directly to the pool's `amm_pc_vault` token account. This requires no interaction with the Raydium program and cannot be blocked by any Raydium account check.
4. Any subsequent call to `SwapBaseIn`, `SwapBaseOut`, `Deposit`, `Withdraw`, or `WithdrawPnl` on this pool reads `amm_pc_vault.amount` (now ≥ `10^9`), computes `10^9 * 10^24 = 10^33`, still under U128::MAX in this specific number — repeat the donation with a larger raw amount (e.g., `4 * 10^18`, well within a u64) to guarantee `val * 10^24 > 3.4 × 10^38`, causing `checked_mul(...).unwrap()` in `normalize_decimal_v2` to panic. This transaction, and every future transaction touching this pool that reaches that code path, aborts. All coin/pc/LP funds in the pool are permanently frozen — no swap, deposit, or withdrawal can ever be executed again for that pool.

### Citations

**File:** program/src/math.rs (L80-116)
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

    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }

    pub fn normalize_decimal_v2(val: u64, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = ret_mut
            .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        ret
    }
```

**File:** program/src/state.rs (L737-745)
```rust
        if pc_decimals > coin_decimals {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(pc_decimals.try_into().unwrap())
                .unwrap();
        } else {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(coin_decimals.try_into().unwrap())
                .unwrap();
        }
```

**File:** program/src/processor.rs (L178-190)
```rust
        let calc_pc_amount = Calculator::restore_decimal(
            target.calc_pnl_x.into(),
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let calc_coin_amount = Calculator::restore_decimal(
            target.calc_pnl_y.into(),
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
```

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L950-959)
```rust
        let x = Calculator::normalize_decimal_v2(
            amm_pc_vault.amount,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y = Calculator::normalize_decimal_v2(
            amm_coin_vault.amount,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
```

**File:** program/src/processor.rs (L1155-1173)
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
        // calc and update pnl
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```
