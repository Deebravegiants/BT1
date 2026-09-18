### Title
Unvalidated mint decimals cause unconditional panic in decimal-normalization math, permanently freezing pool funds - ([File: program/src/math.rs])

### Summary
Analogous to the Ella Core NGAP PDU-Session-ID bug (an out-of-range field value from attacker-controlled input reaching an unchecked path and causing a panic), Raydium's `Calculator::normalize_decimal`, `Calculator::normalize_decimal_v2`, and `Calculator::restore_decimal` compute `10^native_decimal` with `.unwrap()` on a `checked_pow` call, with no upper-bound validation of `native_decimal`. `native_decimal` is populated from `amm.pc_decimals` / `amm.coin_decimals`, which are ultimately derived from the SPL Mint `decimals` field of the coin/pc mints supplied by whoever creates the pool via `Initialize2`. Any pool creator can supply a mint whose `decimals` value is large enough that `10^decimals` overflows a 128-bit integer, turning `checked_pow` into `None` and the subsequent `.unwrap()` into a panic.

### Finding Description
`Calculator::normalize_decimal_v2` and `Calculator::restore_decimal` both compute: [1](#0-0) [2](#0-1) 

`U128` is a 128-bit integer type (`construct_uint! { pub struct U128(2); }`), whose maximum representable value is roughly `3.4×10^38`. `checked_pow` on `U128::from(10)` therefore returns `None` once the exponent (`native_decimal`) exceeds ~38, and the code immediately calls `.unwrap()` on that `None`, panicking the program.

`native_decimal` here is `amm.pc_decimals` / `amm.coin_decimals`, values that are stored on the `AmmInfo` account at pool initialization time and originate from the SPL token mint's `decimals` field — a `u8` that can legally hold any value from 0–255 for a custom mint. A pool creator invoking `Initialize2` can supply an arbitrary SPL mint (there is no whitelist or decimals sanity check enforced by the AMM program on the mint accounts) with `decimals` set to, e.g., 200. Because these normalization routines are invoked repeatedly for pnl accounting (`calc_take_pnl`, `process_withdrawpnl`) using `amm.pc_decimals` / `amm.coin_decimals`: [3](#0-2) 

any subsequent instruction that reaches `calc_take_pnl` (deposit, withdraw, withdraw-pnl paths) for that pool will deterministically panic and abort, because the same oversized decimals value is used on every call.

This mirrors the Ella Core CWE-129 pattern precisely: a numeric field from attacker-influenced input (PDU Session ID / token decimals) is used directly in a computation path (array/PDU processing / exponentiation) without a range check, and an out-of-range value drives the program into an unreachable/`unwrap`-panicking branch.

### Impact Explanation
Once a pool is created with a mint whose `decimals` exceeds the safe exponent range, every instruction that routes through `calc_take_pnl`/`normalize_decimal_v2`/`restore_decimal` for that pool (deposit, withdraw, withdraw-pnl) will panic and fail. Because these accounting routines run on every deposit/withdraw against the AMM's vaults, any liquidity subsequently deposited into that pool by unsuspecting LPs becomes permanently stuck: withdrawals from that pool can never succeed since the same panicking code path executes for a withdrawal. This satisfies the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
Any unprivileged user can create such a malicious pool by calling `Initialize2` (`process_initialize2` in `program/src/processor.rs`) with a self-issued SPL mint configured with extreme decimals (0–255 is valid for the SPL Token program, no runtime check in raydium-amm restricts this). No elevated privileges, validator collusion, or off-chain component is required — the entire attack is a single `Initialize2` transaction followed by ordinary deposit/withdraw transactions from any third party who is lured into providing liquidity to the pool.

### Recommendation
Validate `pc_decimals`/`coin_decimals` (and any other externally supplied decimal-like fields) at `Initialize2` time to fall within a safe bound (e.g., ≤ 19, since `U128` safely supports powers of 10 up to `10^38`), rejecting pool creation for mints outside that bound. Additionally, replace the `.unwrap()` calls on `checked_pow`/`checked_mul`/`checked_div` in `Calculator::normalize_decimal`, `normalize_decimal_v2`, and `restore_decimal` with proper `Result` propagation (`ok_or(AmmError::...)?`) so any future overflow condition returns a program error instead of panicking.

### Proof of Concept
1. Attacker creates two SPL mints: `coin_mint` with `decimals = 9` (normal) and `pc_mint` with `decimals = 200` (crafted), using the standard SPL Token program (no special privileges required).
2. Attacker calls `Initialize2` (`raydium_amm::instruction::initialize2` / `Processor::process_initialize2`) to create a new AMM pool using these mints; `amm.pc_decimals` is set to `200`.
3. A victim LP calls `Deposit` into this pool. `process_deposit` eventually invokes `Self::calc_take_pnl`, which calls `Calculator::restore_decimal(target.calc_pnl_x.into(), amm.pc_decimals, amm.sys_decimal_value)`: [4](#0-3) 
   Internally this executes `U128::from(10).checked_pow(200.into())`, which overflows `U128`'s 128-bit capacity, returns `None`, and the subsequent `.unwrap()` in `restore_decimal` panics: [5](#0-4) 
4. The transaction fails with a panic. Every subsequent `Deposit`/`Withdraw`/`WithdrawPnl` call against this pool panics identically, permanently locking any tokens already deposited into the pool's vaults.

### Citations

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

**File:** program/src/processor.rs (L178-187)
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
```
