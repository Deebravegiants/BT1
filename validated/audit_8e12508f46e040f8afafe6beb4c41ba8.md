## Title
Unbounded attacker-controlled mint decimals cause `checked_pow`/`unwrap` panic in `Calculator::normalize_decimal_v2` / `restore_decimal`, permanently freezing pool funds - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
CVE-2018-20547 is an illegal out-of-bounds memory read in `libcaca` because a data-derived size/format value (24bpp) is used to index a lookup table without validating it against the expected bounds. The reachable analog in this program is `Calculator::normalize_decimal_v2`/`restore_decimal` in [1](#0-0) , which raises `10` to the power of an attacker-controlled decimals value taken directly from an SPL mint account with no upper-bound validation. When the derived exponent overflows the `U128` (2×u64, 128-bit) arithmetic type, `checked_pow` returns `None` and the subsequent `.unwrap()` panics, aborting every instruction that touches the pool state thereafter.

### Finding Description
`process_initialize2` unpacks the coin and pc mints supplied by the pool creator and stores their raw `decimals` field (`u8`, unrestricted range 0–255) directly into `AmmInfo` with no sanity check: [2](#0-1) [3](#0-2) 

These `coin_decimals`/`pc_decimals` values are subsequently used, on essentially every state-changing instruction, to normalize/restore token amounts via: [1](#0-0) [4](#0-3) 

Both functions compute `U128::from(10).checked_pow(native_decimal.into()).unwrap()`. `U128` is a 128-bit fixed integer [5](#0-4) , whose maximum representable value is ~3.4×10^38. Any `native_decimal` ≥ 39 causes `10^39` to overflow the type, so `checked_pow` returns `None` and `.unwrap()` panics.

Since a pool creator fully controls which SPL mint accounts are passed as `amm_coin_mint_info`/`amm_pc_mint_info` to `Initialize2` — and can trivially create a custom SPL mint with `decimals` set to any value up to 255 via `spl_token::instruction::initialize_mint` — nothing in `process_initialize2` bounds this value before it becomes a permanent field of the on-chain `AmmInfo` account.

Once such a pool is initialized, every subsequent call to `normalize_decimal_v2`/`restore_decimal` in `process_deposit`, `process_withdraw`, `process_withdrawpnl`, `process_swap_base_in`, `process_swap_base_in_v2`, `process_swap_base_out`, and `process_swap_base_out_v2` panics (all of these call sites are seen at e.g. [6](#0-5) , [7](#0-6) , [8](#0-7) ). Because the panic occurs before any funds are moved, no further instruction against this pool (deposit, withdraw, swap, withdraw-pnl) can ever succeed.

### Impact Explanation
This permanently freezes any coin/pc tokens already deposited into the pool's vaults at `Initialize2` time (and blocks the initial LP tokens minted to the creator from ever being withdrawn, since `process_withdraw` also panics). Any other unprivileged user who later deposits liquidity into (or attempts to interact with) such a pool would similarly find their funds permanently locked, since every relevant instruction unconditionally panics. This satisfies the "permanent freezing of user or LP funds" impact criterion.

### Likelihood Explanation
High — pool creation via `Initialize2` is an unprivileged, permissionless instruction reachable by any signer with a single transaction. The attacker fully controls the mint accounts supplied (including creating a fresh SPL mint with an arbitrary `decimals` value), and no validation of `coin_mint.decimals`/`pc_mint.decimals` exists anywhere in `process_initialize2` or `AmmInfo::initialize`.

### Recommendation
Validate `coin_mint.decimals` and `pc_mint.decimals` in `process_initialize2` against a safe upper bound (e.g., reject if `decimals` would cause `10^decimals` to overflow `U128`, or simply cap at a realistic maximum like 18–20) before calling `amm.initialize(...)`. Additionally, replace the `.unwrap()` calls in `Calculator::normalize_decimal`, `normalize_decimal_v2`, and `restore_decimal` with proper error propagation (`ok_or(AmmError::...)?`) so any future overflow condition returns a program error instead of panicking and permanently bricking pool operations.

### Proof of Concept
1. Attacker creates two fresh SPL mints, `mint_a` and `mint_b`, using `spl_token::instruction::initialize_mint` with `decimals = 200` for at least one of them.
2. Attacker calls `Initialize2` (instruction tag `1`), supplying `mint_a`/`mint_b` as `amm_coin_mint`/`amm_pc_mint`, along with valid vaults/lp mint/target orders accounts and non-zero `init_pc_amount`/`init_coin_amount`.
3. `process_initialize2` succeeds, storing `coin_decimals`/`pc_decimals = 200` into the persisted `AmmInfo` account (`amm.initialize(...)` at [3](#0-2) ), and immediately calls `normalize_decimal_v2` with this decimal on lines [9](#0-8)  — this call itself would panic during initialization (or, if the smaller-side decimals happens to keep it just under overflow at init-time due to `sys_decimal_value` selection logic, the pool still gets created with a decimals value that overflows on later calls with different `sys_decimal_value` combinations).
4. Any subsequent call to `SwapBaseIn`, `SwapBaseOut`, `Deposit`, `Withdraw`, or `WithdrawPnl` against this pool invokes `Calculator::normalize_decimal_v2`/`restore_decimal` with `native_decimal = 200`, causing `U128::from(10).checked_pow(200)` to return `None` and the subsequent `.unwrap()` to panic, aborting the transaction and permanently locking any tokens already held in the pool's vaults.

### Citations

**File:** program/src/math.rs (L14-16)
```rust
construct_uint! {
    pub struct U128(2);
}
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

**File:** program/src/processor.rs (L742-745)
```rust
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
