## Analysis Result

### Title
Unchecked subtraction panic in `swap_token_amount_base_out` reachable via `SwapBaseOut`/`SwapBaseOutV2` causes transaction-abort DoS - (File: `program/src/math.rs`)

### Summary
`Calculator::swap_token_amount_base_out` computes the swap input amount using `total_pc_without_take_pnl.checked_sub(amount_out).unwrap()` (and the coin-side equivalent), but the bounds check that would prevent `amount_out` from exceeding the pool's total balance is only performed *after* this calculation, inside the later `match swap_direction` block in `process_swap_base_out`/`process_swap_base_out_v2`. An attacker who submits a `SwapBaseOut`/`SwapBaseOutV2` instruction with an `amount_out` value greater than or equal to the pool's current `total_pc_without_take_pnl` (or `total_coin_without_take_pnl`) triggers a `checked_sub` underflow, `unwrap()`s to `None`, and panics the program.

### Finding Description
`swap_token_amount_base_out` blindly `unwrap()`s a `checked_sub`: [1](#0-0) 

This helper is invoked by `process_swap_base_out` and `process_swap_base_out_v2` to determine the required input amount from the caller-supplied `swap.amount_out`. The actual guard against `amount_out` being too large (`if swap.amount_out >= total_pc_without_take_pnl { return Err(AmmError::InsufficientFunds.into()); }`) is only executed later, inside the `match swap_direction` block used for performing the token transfers: [2](#0-1) [3](#0-2) 

The same unsafe pattern repeats in `process_swap_base_out_v2`, which has an even simpler, unprivileged account layout (no market/open-orders accounts needed): [4](#0-3) 

Because `swap_token_amount_base_out`'s subtraction runs before the `>=` bound check, when `swap.amount_out` is set (by the caller) to a value `>= total_pc_without_take_pnl` (or the coin equivalent for the reverse direction), the subtraction in `math.rs` underflows and `.unwrap()` panics, aborting the transaction with a runtime panic rather than returning the intended `AmmError::InsufficientFunds`.

This is directly analogous to CVE-2019-8382's root cause class: a value returned from a lookup/calculation is used before validating that the operation could safely occur (`AP4_List::Find` returning null and being dereferenced without a null check; here, a value that can legitimately be `None` after `checked_sub` is `unwrap()`ed before the corresponding validity check executes).

### Impact Explanation
Any unprivileged caller can trigger a Rust panic in the on-chain program by submitting a single `SwapBaseOut` or `SwapBaseOutV2` transaction with `amount_out` set at or above the pool's real total balance for the corresponding side. This crashes/aborts the instruction execution path with a panic instead of the intended graceful `InsufficientFunds` error. While Solana's runtime contains panics to the failing transaction (it does not crash validators), this is a reachable, attacker-controlled Denial-of-Service condition against a core, unprivileged, user-facing instruction (swap) that undermines the intended error-handling contract of the AMM and can be used to grief or probe pool state deterministically. It does not by itself cause direct fund loss.

### Likelihood Explanation
High likelihood of triggering: the attacker only needs to know (or query) the current vault balances (`amm_coin_vault`/`amm_pc_vault`, both public accounts) and pick `amount_out` at or above the corresponding `total_..._without_take_pnl` value, then sign and submit a standard `SwapBaseOut`/`SwapBaseOutV2` instruction with their own token accounts. No privileged signer, special build, or off-chain dependency is required.

### Recommendation
Move (or duplicate) the `amount_out >= total_pc_without_take_pnl` / `amount_out >= total_coin_without_take_pnl` bound checks to occur *before* calling `Calculator::swap_token_amount_base_out`, and additionally harden `swap_token_amount_base_out` itself to use `checked_sub(...).ok_or(AmmError::InsufficientFunds)?` (propagating a proper program error) instead of `.unwrap()`, so that out-of-range `amount_out` values always produce a controlled `ProgramResult::Err` rather than a panic.

### Proof of Concept
1. Create/observe a Raydium AMM pool and read its `amm_coin_vault_info`/`amm_pc_vault_info` balances to determine `total_pc_without_take_pnl` (approximately vault balance minus `need_take_pnl_pc`).
2. Construct a `SwapBaseOutV2` instruction (`program/src/instruction.rs`, `SwapBaseOutV2`) targeting that pool, with attacker-owned `user_source_info`/`user_destination_info` token accounts, setting `swap.amount_out` equal to or greater than the observed `total_pc_without_take_pnl` (choosing the PC2Coin/Coin2PC direction consistent with mints).
3. Submit the transaction; execution reaches `process_swap_base_out_v2` → `Calculator::swap_token_amount_base_out` (`program/src/math.rs:335-347`) before the `swap.amount_out >= total_pc_without_take_pnl` guard is checked in the `match` block (`program/src/processor.rs:2591-2595`), causing `checked_sub(...).unwrap()` to panic and the transaction to abort with a runtime panic instead of the intended `AmmError::InsufficientFunds`.

### Citations

**File:** program/src/math.rs (L335-347)
```rust
            SwapDirection::Coin2PC => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (coin + amount_in) * (pc - amount_out) = coin * pc
                // => amount_in = coin * pc / (pc - amount_out) - coin
                // => amount_in = (coin * pc - pc * coin + amount_out * coin) / (pc - amount_out)
                // => amount_in = (amount_out * coin) / (pc - amount_out)
                let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_coin_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
            }
```

**File:** program/src/processor.rs (L2212-2216)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/processor.rs (L2455-2519)
```rust
    pub fn process_swap_base_out_v2(
        program_id: &Pubkey,
        accounts: &[AccountInfo],
        swap: SwapInstructionBaseOut,
    ) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        let token_program_info = next_account_info(account_info_iter)?;
        let amm_info = next_account_info(account_info_iter)?;
        let amm_authority_info = next_account_info(account_info_iter)?;
        let amm_coin_vault_info = next_account_info(account_info_iter)?;
        let amm_pc_vault_info = next_account_info(account_info_iter)?;
        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if amm.pc_vault_mint == amm.coin_vault_mint {
            return Err(AmmError::NotAllowed.into());
        }
        let user_source_info = next_account_info(account_info_iter)?;
        let user_destination_info = next_account_info(account_info_iter)?;
        let user_source_owner = next_account_info(account_info_iter)?;
        if !user_source_owner.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }

        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let spl_token_program_id = token_program_info.key;
        let authority = Self::authority_id(program_id, AUTHORITY_AMM, amm.nonce as u8)?;
        check_assert_eq!(
            *amm_authority_info.key,
            authority,
            "authority",
            AmmError::InvalidProgramAddress
        );
        check_assert_eq!(
            *amm_coin_vault_info.key,
            amm.coin_vault,
            "coin_vault",
            AmmError::InvalidCoinVault
        );
        check_assert_eq!(
            *amm_pc_vault_info.key,
            amm.pc_vault,
            "pc_vault",
            AmmError::InvalidPCVault
        );

        if *user_source_info.key == amm.pc_vault || *user_source_info.key == amm.coin_vault {
            return Err(AmmError::InvalidUserToken.into());
        }
        if *user_destination_info.key == amm.pc_vault
            || *user_destination_info.key == amm.coin_vault
        {
            return Err(AmmError::InvalidUserToken.into());
        }

        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;

        let user_source = Self::unpack_token_account(&user_source_info, spl_token_program_id)?;
        let user_destination =
            Self::unpack_token_account(&user_destination_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L2591-2595)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```
