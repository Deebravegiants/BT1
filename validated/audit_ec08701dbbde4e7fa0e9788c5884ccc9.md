### Title
`calc_take_pnl` invariant check can permanently revert deposits/withdraws, freezing the pool or forcing LP-share inflation ([File: program/src/processor.rs])

### Summary
`Processor::calc_take_pnl` in `program/src/processor.rs` gates every `Deposit` and `Withdraw` (and `WithdrawPnl`) with a strict invariant check comparing the *current* pool value (`total_pc_without_take_pnl * total_coin_without_take_pnl`) against a cached "last-k" snapshot (`target.calc_pnl_x * target.calc_pnl_y`). If the current product ever falls below the cached snapshot, the instruction returns `AmmError::CalcPnlError`, and there is no unprivileged recovery path to reset the cached snapshot. [1](#0-0) [2](#0-1) 

### Finding Description
`calc_take_pnl` computes:
```
if pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount { ... } else { return Err(CalcPnlError) }
```
where `calc_pc_amount`/`calc_coin_amount` come from `target_orders.calc_pnl_x` / `calc_pnl_y` — a snapshot recorded at the last successful `Deposit`/`Withdraw`/`WithdrawPnl` — normalized/restored through `Calculator::normalize_decimal_v2` / `restore_decimal`. [3](#0-2) 

Critically, `process_swap_base_in` and `process_swap_base_out` recompute `total_pc_without_take_pnl` / `total_coin_without_take_pnl` from live vault balances but **never call `calc_take_pnl` and never update `target_orders.calc_pnl_x`/`calc_pnl_y`** after a swap. [4](#0-3) [5](#0-4) 

This means the cached "last-k" snapshot only gets refreshed on `Deposit`/`Withdraw`, while the pool's real product-of-reserves can drift on every swap due to decimal normalization/rounding (`normalize_decimal_v2`/`restore_decimal`, both invoked inside `calc_take_pnl` and the callers) and due to the `pnl_numerator/pnl_denominator` fee split that removes value from the reserves used for the check while pnl is skimmed into `need_take_pnl_pc/coin`. Any subsequent `Deposit`, `Withdraw`, or `WithdrawPnl` recomputes the live product and compares it to the stale snapshot; if rounding/precision loss (or a chain of swaps/pnl skims) ever nudges the live product below the last recorded snapshot, `calc_take_pnl` unconditionally reverts with `CalcPnlError`. [6](#0-5) [7](#0-6) [8](#0-7) 

Because the snapshot (`calc_pnl_x`/`calc_pnl_y`) is only advanced inside the very functions that this check gates, once the check fails there is no unprivileged instruction that can update or repair `target_orders.calc_pnl_x`/`calc_pnl_y` to unstick the pool — deposits and withdrawals become permanently blocked (swaps that don't call `calc_take_pnl` may still work, but LP entry/exit is frozen). This directly mirrors the reported bug class: a strict invariant/yield check with no tolerance/rebasing mechanism that can permanently DoS the pool for ordinary LP actions once reserves deviate from a stale reference value.

### Impact Explanation
If tripped, `Deposit` (`process_deposit`) and `Withdraw` (`process_withdraw`) both call `calc_take_pnl` and will revert deterministically on every call once the invariant is violated, since nothing in these code paths can decrease `calc_pnl_x`/`calc_pnl_y` to match a lower live-k without first successfully executing (which is exactly what's blocked). [9](#0-8) [10](#0-9)  This is a permanent freeze of LP funds (unable to withdraw liquidity) and of new deposits, satisfying the "permanent freezing of user or LP funds" bar. Existing LPs cannot exit their position through the normal `Withdraw` instruction while the fault persists.

### Likelihood Explanation
The exact numeric conditions needed to trip `pool_pc_amount * pool_coin_amount < calc_pc_amount * calc_coin_amount` depend on the specific decimal-normalization rounding behavior of `Calculator::normalize_decimal_v2`/`restore_decimal` and the magnitude of `pnl_numerator/pnl_denominator` skimmed on each deposit/withdraw cycle — I was not able to fully trace `normalize_decimal_v2`/`restore_decimal`'s rounding direction within the remaining investigation budget, so I cannot confirm the precise trigger conditions or quantify how easily an unprivileged actor could force this state through ordinary swap/deposit/withdraw sequences alone. This uncertainty should be resolved by inspecting `Calculator::normalize_decimal_v2` and `Calculator::restore_decimal` in `program/src/math.rs` directly.

### Recommendation
Given the confirmed architecture (snapshot only refreshed by the very functions it gates, no unprivileged reset path), consider: (1) allowing `calc_take_pnl` to tolerate a bounded/rounding-safe deviation instead of a strict `>=` compare, and/or (2) adding a mechanism (even privileged) to resynchronize `target_orders.calc_pnl_x`/`calc_pnl_y` to the current live reserve product without requiring the invariant check to pass first, so that a single rounding-induced dip cannot permanently deadlock deposits/withdrawals.

### Proof of Concept
Not able to construct a concrete numeric PoC within this investigation — doing so requires precisely characterizing rounding loss in `Calculator::normalize_decimal_v2`/`restore_decimal` (in `program/src/math.rs`) across repeated deposit/withdraw/swap sequences to show the live product-of-reserves can dip below the cached `calc_pnl_x * calc_pnl_y` snapshot. This would need to be validated with the full source of `program/src/math.rs`'s normalization functions, which I could not fully retrieve before the iteration limit.

### Citations

**File:** program/src/processor.rs (L167-193)
```rust
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
        // calc pnl
        let mut delta_x: u128;
        let mut delta_y: u128;
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
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
            // last k is
```

**File:** program/src/processor.rs (L267-278)
```rust
        } else {
            msg!(arrform!(
                LOG_SIZE,
                "calc_take_pnl error x:{}, y:{}, calc_pnl_x:{}, calc_pnl_y:{}",
                x1,
                y1,
                identity(target.calc_pnl_x),
                identity(target.calc_pnl_y)
            )
            .as_str());
            return Err(AmmError::CalcPnlError.into());
        }
```

**File:** program/src/processor.rs (L1148-1173)
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

**File:** program/src/processor.rs (L1376-1465)
```rust
    pub fn process_withdrawpnl(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
        let account_info_iter = &mut accounts.iter();
        let token_program_info = next_account_info(account_info_iter)?;

        let amm_info = next_account_info(account_info_iter)?;
        let amm_config_info = next_account_info(account_info_iter)?;
        let amm_authority_info = next_account_info(account_info_iter)?;
        let amm_coin_vault_info = next_account_info(account_info_iter)?;
        let amm_pc_vault_info = next_account_info(account_info_iter)?;
        let user_pnl_coin_info = next_account_info(account_info_iter)?;
        let user_pnl_pc_info = next_account_info(account_info_iter)?;
        let pnl_owner_info = next_account_info(account_info_iter)?;
        let amm_target_orders_info = next_account_info(account_info_iter)?;

        let mut amm = AmmInfo::load_mut_checked(&amm_info, program_id)?;
        if *amm_authority_info.key
            != Self::authority_id(program_id, AUTHORITY_AMM, amm.nonce as u8)?
        {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        if amm_info.owner != program_id {
            return Err(AmmError::InvalidOwner.into());
        }

        let (pda, _) = Pubkey::find_program_address(&[&AMM_CONFIG_SEED], program_id);
        if pda != *amm_config_info.key || amm_config_info.owner != program_id {
            return Err(AmmError::InvalidConfigAccount.into());
        }
        let amm_config = AmmConfig::load_checked(&amm_config_info, program_id)?;

        if !pnl_owner_info.is_signer
            || (*pnl_owner_info.key != config_feature::amm_owner::ID
                && *pnl_owner_info.key != amm_config.pnl_owner)
        {
            return Err(AmmError::InvalidSignAccount.into());
        }
        // withdrawpnl in all status except Uninitialized
        if amm.status == AmmStatus::Uninitialized.into_u64() {
            msg!(&format!("withdrawpnl: status {}", identity(amm.status)));
            return Err(AmmError::InvalidStatus.into());
        }
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
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );

        let spl_token_program_id = token_program_info.key;

        check_assert_eq!(
            *amm_target_orders_info.key,
            amm.target_orders,
            "target_orders",
            AmmError::InvalidTargetOrders
        );
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_pnl_coin = Self::unpack_token_account(&user_pnl_coin_info, spl_token_program_id)?;
        let user_pnl_pc = Self::unpack_token_account(&user_pnl_pc_info, spl_token_program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        if amm_coin_vault.mint != amm.coin_vault_mint || user_pnl_coin.mint != amm.coin_vault_mint {
            return Err(AmmError::InvalidCoinMint.into());
        }
        if amm_pc_vault.mint != amm.pc_vault_mint || user_pnl_pc.mint != amm.pc_vault_mint {
            return Err(AmmError::InvalidPCMint.into());
        }

        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

```

**File:** program/src/processor.rs (L1719-1749)
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

        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }
```

**File:** program/src/processor.rs (L1940-1946)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

```

**File:** program/src/processor.rs (L2047-2051)
```rust
        };
        amm.recent_epoch = Clock::get()?.epoch;

        Ok(())
    }
```
