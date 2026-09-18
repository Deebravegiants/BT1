Confirmed: `coin_mint.decimals` and `pc_mint.decimals` are taken directly from attacker-supplied SPL mint accounts with no bounds check, at [1](#0-0) . Since a pool creator can mint their own coin/pc mints with an arbitrary `decimals` byte (0–255), and `normalize_decimal_v2`/`restore_decimal` compute `10u128.checked_pow(native_decimal)` with `.unwrap()` on every swap, deposit, withdraw, and pnl calculation, this is a real, reachable panic/DoS path — not the CVE's SQL engine bug, but a genuine analog in the "crafted data causes DoS" bug class.

### Title
Attacker-controlled mint `decimals` causes `checked_pow`/`unwrap()` panic, permanently freezing pool funds - (File: program/src/math.rs, program/src/processor.rs)

### Summary
`Calculator::normalize_decimal_v2` and `Calculator::restore_decimal` compute `10u128.checked_pow(native_decimal)` and then `.unwrap()` the result [2](#0-1) [3](#0-2) . `native_decimal` is populated directly from the SPL mint `decimals` field of the coin/pc mint supplied by the pool creator during `Initialize2`, with no upper-bound validation [1](#0-0) .

### Finding Description
`process_initialize2` unpacks the coin and pc mints supplied by the caller and passes their raw `decimals` byte straight into `amm.initialize(...)`, which stores them as `amm.coin_decimals`/`amm.pc_decimals` [4](#0-3) . There is no check that `decimals` stays within a sane bound (e.g., ≤ 19, since `10^20` already overflows `u128`).

Every subsequent instruction that touches this pool — `process_deposit`, `process_withdraw`, `process_withdrawpnl`, `process_swap_base_in[_v2]`, `process_swap_base_out[_v2]` — calls `Calculator::normalize_decimal_v2`/`restore_decimal` with `amm.coin_decimals`/`amm.pc_decimals`, e.g. [5](#0-4)  and [6](#0-5) . Internally this computes `U128::from(10).checked_pow(native_decimal.into()).unwrap()`. `U128` is 128 bits (max ≈ 3.4×10^38), so any `decimals` value ≥ 39 makes `checked_pow` return `None`, and the subsequent `.unwrap()` panics, aborting the transaction.

Because a pool creator fully controls the coin/pc mint accounts passed into `Initialize2` (they can create their own SPL mints with `decimals` set to any `u8` value, e.g., 200), they can create a pool whose `amm.coin_decimals` or `amm.pc_decimals` is set to an out-of-range value. Once such a pool exists, every swap, deposit, and withdraw against it will panic in the decimal-normalization step before any economic effect happens, meaning:
- Any legitimate LP who is later lured to deposit into (or already has funds in) that pool cannot withdraw, because `process_withdraw` and `process_withdrawpnl` both call `normalize_decimal_v2` before doing the token transfer [7](#0-6) .
- There's no path in the on-chain program to change `coin_decimals`/`pc_decimals` after initialization, so once tokens are deposited (via `Initialize2`'s mandatory initial `init_pc_amount`/`init_coin_amount` transfer at lines 835-841) into vaults of a pool with an out-of-range decimals value, they are permanently locked in the vault PDA — no instruction can reach a successful completion to move them out.

### Impact Explanation
This matches "permanent freezing of user or LP funds": the pool's own vaults hold `init_pc_amount`/`init_coin_amount` tokens transferred in during `Initialize2`, and no instruction (swap, deposit, withdraw, withdrawpnl) can complete without panicking, so those funds are unrecoverable via the program's own instruction set. If other users are tricked into depositing into this pool (a plausible scenario for pools on any permissionless AMM UI/aggregator), their funds are frozen the same way.

### Likelihood Explanation
Likelihood is limited by the fact that the attacker must be the pool creator (able to mint their own coin/pc mint), which is unprivileged but self-limits blast radius to funds deposited into *that specific* pool (their own initial funds, and any LP funds a third party later adds to that same pool, e.g., automated market-making bots or LPs who don't verify decimals before depositing). It does not corrupt other pools.

### Recommendation
Add an explicit bound check on `coin_mint.decimals` and `pc_mint.decimals` in `process_initialize2` (e.g., reject if `decimals > 18` or any value that would make `10^decimals` fit safely within the `U128`/`u64` arithmetic used throughout `math.rs`), and replace the `.unwrap()` calls in `normalize_decimal_v2`/`restore_decimal`/`normalize_decimal` with propagated `AmmError` results instead of panics, so malformed state can't cause a permanent abort.

### Proof of Concept
1. Attacker creates two SPL mints, `coin_mint` with `decimals = 200` and a normal `pc_mint`.
2. Attacker calls `Initialize2` with these mints; `process_initialize2` accepts them since there is no decimals bound check [8](#0-7) , and `amm.coin_decimals` is set to 200 [1](#0-0) . The initial `init_coin_amount`/`init_pc_amount` tokens are transferred into the vaults before this point (lines ~835-841 execute a `token_transfer` prior to the decimals-dependent computation at line 950).
3. Any subsequent `SwapBaseIn`, `SwapBaseOut`, `Deposit`, `Withdraw`, or `WithdrawPnl` call against this pool invokes `Calculator::normalize_decimal_v2(_, 200, sys_decimal_value)`, which calls `U128::from(10).checked_pow(200.into())` → overflow → `None` → `.unwrap()` panics, reverting the transaction. No instruction can ever succeed against this pool, permanently freezing the initial vault balances and any subsequently deposited LP funds.

### Citations

**File:** program/src/processor.rs (L717-745)
```rust
        if amm_config.create_pool_fee != 0 {
            invoke(
                &system_instruction::transfer(
                    user_wallet_info.key,
                    create_fee_destination_info.key,
                    amm_config.create_pool_fee,
                ),
                &[
                    user_wallet_info.clone(),
                    create_fee_destination_info.clone(),
                    system_program_info.clone(),
                ],
            )?;
            invoke(
                &spl_token::instruction::sync_native(
                    token_program_info.key,
                    create_fee_destination_info.key,
                )?,
                &[
                    token_program_info.clone(),
                    create_fee_destination_info.clone(),
                ],
            )?;
        }

        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L931-938)
```rust
        amm.initialize(
            init.nonce,
            init.open_time,
            coin_mint.decimals,
            pc_mint.decimals,
            0,
            0,
        )?;
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

**File:** program/src/processor.rs (L1352-1361)
```rust
        target_orders.calc_pnl_x = x1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_pc_amount,
                amm.pc_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
            .checked_sub(U128::from(delta_x))
            .unwrap()
            .as_u128();
```

**File:** program/src/processor.rs (L1726-1735)
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

**File:** program/src/math.rs (L96-104)
```rust
    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }
```

**File:** program/src/math.rs (L106-116)
```rust
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
