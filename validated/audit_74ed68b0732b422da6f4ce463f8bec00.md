### Title
Panic-inducing integer overflow (`checked_pow`/`.unwrap()`) in decimal-normalization math when a pool is created with an attacker-controlled high-decimals mint - (File: `program/src/math.rs`)

### Summary
`Calculator::normalize_decimal`, `Calculator::normalize_decimal_v2`, and `Calculator::restore_decimal` compute `U128::from(10).checked_pow(native_decimal.into())` and immediately call `.unwrap()` on the result, with no fallback to a `Status`-like error path. `native_decimal` is derived from the coin/PC SPL mint's `decimals` field, which is fully attacker-controlled when a pool is created via `Initialize2` with an arbitrary mint. This mirrors the reported TensorFlow bug class (CWE-190): an unchecked arithmetic operation that returns `None`/negative on overflow is blindly unwrapped/`CHECK`-ed instead of being propagated as an error, turning attacker-influenceable input into a program panic.

### Finding Description
`math.rs` performs:
```
U128::from(10).checked_pow(native_decimal.into()).unwrap()
```
in three places: `normalize_decimal` [1](#0-0) , `restore_decimal` [2](#0-1) , and `normalize_decimal_v2` [3](#0-2) .

`U128::MAX` is roughly `3.4 × 10^38`. `10^decimals` exceeds that bound once `decimals ≥ 39`, which returns `None` from `checked_pow`, and the subsequent `.unwrap()` panics the on-chain program — an analog to the `CHECK`-failure crash described in the TensorFlow advisory, where an unchecked overflow (`MultiplyWithoutOverflow`/`AddDim`) leads to a hard crash instead of a recoverable `Status`/error.

`native_decimal` comes from `amm.coin_decimals` / `amm.pc_decimals`, which are populated from the coin/PC mint accounts supplied to `Initialize2`. The SPL `Mint.decimals` field is a `u8` (range 0–255) with no validation in this codebase restricting it to realistic values (e.g. ≤9 or ≤18). A pool creator (an unprivileged, in-scope actor per the rules) can mint a custom SPL token with `decimals` set to any value ≥ 39 and use it as the coin or PC mint when calling `Initialize2`. These normalization routines are invoked on essentially every state-mutating path that touches pool accounting — `Deposit` (`target_orders.calc_pnl_x`/`calc_pnl_y` updates) [4](#0-3) , and `Withdraw` (`x1`/`y1` computation and pnl updates) [5](#0-4) , as well as internally in `calc_take_pnl`, which is exercised by every swap and withdraw. Once such a pool exists, any subsequent call to `Deposit`, `Withdraw`, or either swap instruction on that pool will panic inside `normalize_decimal_v2`/`restore_decimal`, aborting the transaction.

### Impact Explanation
If the panic is only reachable after the pool already holds real liquidity (i.e., `Initialize2`'s own accounting does not exercise the same overflow at creation time), then every `Deposit`, `Withdraw`, and swap instruction against that specific pool becomes permanently unusable — a `CHECK`-fail-style denial of service that permanently freezes any coin/PC/LP funds already locked in that pool's vaults, since no further instruction can succeed to move them out. This satisfies the "permanent freezing of user or LP funds" impact bar. The blast radius is confined to pools created with such a malicious mint, but nothing in `Initialize2`'s account/decimals validation prevents an attacker from creating one and enticing LPs to deposit before the flaw is discovered.

### Likelihood Explanation
Reachability is high: creating an SPL mint with an arbitrary `decimals` value is a standard, permissionless operation, and `Initialize2` accepts attacker-chosen mint accounts as part of a single submitted transaction with no bound-checking on `decimals`. No privileged signer or off-chain component is required — this fits squarely in the in-scope unprivileged pool-creator/LP/swapper threat model.

### Recommendation
- Validate mint `decimals` at `Initialize2` time and reject values that would make `10^decimals` overflow the arithmetic type used downstream (e.g., cap at a sane maximum such as 18, matching realistic token standards).
- Replace the `.unwrap()` calls in `Calculator::normalize_decimal`, `Calculator::restore_decimal`, and `Calculator::normalize_decimal_v2` with proper `checked_pow`/`checked_mul`/`checked_div` chains that propagate an `AmmError` (e.g., `AmmError::CalculationExRateFailure`) instead of panicking, consistent with the "Status"-based pattern recommended in the referenced TensorFlow fix.

### Proof of Concept
1. Attacker creates a new SPL mint `M` with `decimals = 39` (or higher) using the standard SPL Token Program (no special privileges needed).
2. Attacker calls `Initialize2` [6](#0-5)  using `M` as the coin (or PC) mint, providing the required signer/authority accounts as a normal pool creator.
3. `amm.coin_decimals` (or `pc_decimals`) is set to 39.
4. Any subsequent `Deposit` or `Withdraw` call on this pool reaches `Calculator::normalize_decimal_v2` with `native_decimal = 39` [7](#0-6) , `checked_pow` returns `None`, and `.unwrap()` panics, aborting the instruction and leaving any deposited funds unreachable through the normal instruction set for that pool.

### Citations

**File:** program/src/math.rs (L86-90)
```rust
        let ret = Self::to_u64(
            ret_mut
                .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
                .unwrap()
                .as_u128(),
```

**File:** program/src/math.rs (L99-102)
```rust
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
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

**File:** program/src/processor.rs (L1352-1368)
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
        target_orders.calc_pnl_y = y1
            .checked_add(Calculator::normalize_decimal_v2(
                deduct_coin_amount,
                amm.coin_decimals,
                amm.sys_decimal_value,
            ))
            .unwrap()
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

**File:** program/src/instruction.rs (L142-165)
```rust
    ///   Initializes a new AMM pool.
    ///
    ///   0. `[]` Spl Token program id
    ///   1. `[]` Associated Token program id
    ///   2. `[]` Sys program id
    ///   3. `[]` Rent program id
    ///   4. `[writable]` New AMM Account to create.
    ///   5. `[]` $authority derived from `create_program_address(&[AUTHORITY_AMM, &[nonce]])`.
    ///   6. `[writable]` AMM open orders Account
    ///   7. `[writable]` AMM lp mint Account
    ///   8. `[]` AMM coin mint Account
    ///   9. `[]` AMM pc mint Account
    ///   10. `[writable]` AMM coin vault Account. Must be non zero, owned by $authority.
    ///   11. `[writable]` AMM pc vault Account. Must be non zero, owned by $authority.
    ///   12. `[writable]` AMM target orders Account. To store plan orders informations.
    ///   13. `[]` AMM config Account, derived from `find_program_address(&[&&AMM_CONFIG_SEED])`.
    ///   14. `[]` AMM create pool fee destination Account
    ///   15. `[]` Market program id
    ///   16. `[writable]` Market Account. Market program is the owner.
    ///   17. `[writable, signer]` User wallet Account
    ///   18. `[]` User token coin Account
    ///   19. '[]` User token pc Account
    ///   20. `[writable]` User destination lp token ATA Account
    Initialize2(InitializeInstruction2),
```
