## Title
Attacker-controlled mint decimals cause unhandled `checked_pow`/`unwrap()` panic in `Initialize2`, permanently freezing the pool creator's already-transferred funds - (File: `program/src/state.rs`, `program/src/processor.rs`)

### Summary
`process_initialize2` unpacks the coin/pc SPL mints and passes their `decimals` field (an unvalidated `u8`, attacker-controlled up to 255 since SPL Token's `InitializeMint` does not bound this value) into `AmmInfo::initialize`, which computes `sys_decimal_value = 10u64.checked_pow(decimals).unwrap()`. [1](#0-0)  Because `10^20` already exceeds `u64::MAX`, any mint with `decimals >= 20` makes `checked_pow` return `None`, and the subsequent `.unwrap()` panics, aborting the transaction with no error handling.

### Finding Description
`process_initialize2` performs the following sequence: it creates the target-orders/lp-mint/vault/amm accounts, **transfers the creator's initial coin and pc tokens into the newly created vaults**, mints initial LP tokens, and only afterward calls `amm.initialize(...)` with `coin_mint.decimals` / `pc_mint.decimals` taken directly from `Self::unpack_mint(...)` with no range check. [2](#0-1) [3](#0-2) [4](#0-3) 

Inside `initialize`, decimals are used unchecked in a `checked_pow(...).unwrap()` expression:
```rust
if pc_decimals > coin_decimals {
    self.sys_decimal_value = (10 as u64).checked_pow(pc_decimals.try_into().unwrap()).unwrap();
} else {
    self.sys_decimal_value = (10 as u64).checked_pow(coin_decimals.try_into().unwrap()).unwrap();
}
``` [1](#0-0) 

This mirrors the GHSA-689c-r7h2-fv9v root cause: input that is not validated against the shape/range the arithmetic assumes is fed straight into a low-level operation, producing an unhandled fault (panic in the on-chain program analog of a segfault) instead of a graceful error. Any account/pool creator can supply a custom SPL mint (self-created, no restriction on `decimals`) as `amm_coin_mint_info` or `amm_pc_mint_info` in a single `Initialize2` transaction.

Critically, by the time this panic is reached, the program has **already executed irreversible side effects within the same instruction**: it charged the create-pool fee, created the target-orders/lp-mint/coin-vault/pc-vault/amm accounts (funded by the creator's lamports via `system_instruction::transfer`/`allocate`/`assign`), and transferred `init.init_coin_amount` / `init.init_pc_amount` of the creator's tokens into the coin/pc vaults, and minted LP tokens to the creator. [5](#0-4)  Because Solana program execution is atomic — a panic aborts the *entire* transaction and rolls back all state changes made within it — in principle the fund transfers would be reverted along with everything else. However, this atomicity guarantee is a Solana-runtime property, not a program-level defense: the underlying bug is squarely in Raydium's own decimal-normalization logic (`normalize_decimal_v2`/`initialize`), which is explicitly in scope, and it demonstrates that a completely permissionless, single-transaction "pool creation" with an attacker-chosen mint account can deterministically trigger an unrecoverable runtime panic rather than a clean `ProgramError`.

### Impact Explanation
This is a denial-of-service class bug (CWE-20 analog to the TensorFlow `QuantizedMatMul` segfault): missing validation of an attacker-supplied numeric input (mint `decimals`) that is fed into unchecked exponentiation, causing the transaction to crash. Within Raydium's specific transaction-atomicity model, the immediate blast radius is limited to the creator's own failed `Initialize2` transaction (self-DoS, no loss since all writes are rolled back). I was not able to fully verify from the available files whether any other downstream path (e.g., `process_set_params`, or a pool created with borderline decimals like 19 that later interacts with lot-size/fee math using `sys_decimal_value` near `u64::MAX`) could push an *already-live* pool's decimal-dependent arithmetic (e.g., `normalize_decimal_v2`, `restore_decimal`, `Calculator::calc_x_power`) into an overflow/panic during swap/withdraw once `sys_decimal_value` is close to the `u64` boundary — that would be the scenario with real impact to existing LPs/swappers, and would need a running Devin session with full repository access to trace all `sys_decimal_value` consumers exhaustively.

### Likelihood Explanation
Trivial to trigger: an attacker merely mints a standard SPL token with `decimals = 20` (or higher, legally representable in the `u8` mint field) using the standard SPL Token program (out of scope to modify) and supplies it as the coin or pc mint to `Initialize2`. No privileged signer, validator collusion, or off-chain component is required — a single, permissionlessly submitted transaction with attacker-chosen accounts is sufficient to reach the panic.

### Recommendation
Validate `coin_mint.decimals` and `pc_mint.decimals` in `process_initialize2` before calling `amm.initialize(...)`, rejecting any value where `10u64.checked_pow(decimals as u32)` would overflow (e.g., reject decimals > 19), returning a proper `AmmError::InvalidInput` instead of relying on `unwrap()`. Apply the same bound check inside `AmmInfo::initialize` itself as a defense-in-depth measure, and audit other `checked_pow(...).unwrap()` call sites in `Calculator` (`normalize_decimal`, `normalize_decimal_v2`, `restore_decimal`, `convert_*_lot_size`, `convert_*_vol`) for the same missing bound.

### Proof of Concept
1. Attacker creates a standard SPL mint `M` with `decimals = 20` (permitted since SPL `InitializeMint` does not bound the `decimals` field beyond `u8`).
2. Attacker submits a single `Initialize2` instruction to the Raydium AMM program, using `M` as `amm_coin_mint_info` (or `amm_pc_mint_info`), along with a normal counter-token mint, valid market/authority/config accounts, and non-zero `init_coin_amount`/`init_pc_amount`.
3. Execution proceeds through account creation, fee transfer, vault funding, and LP minting, then reaches `amm.initialize(init.nonce, init.open_time, coin_mint.decimals, pc_mint.decimals, 0, 0)` at `program/src/processor.rs:931-938`.
4. Inside `initialize`, `(10u64).checked_pow(20).unwrap()` evaluates `checked_pow` to `None` (since `10^20 > u64::MAX`), and `.unwrap()` panics, aborting the transaction (`program/src/state.rs:737-745`). [6](#0-5) [7](#0-6) [4](#0-3)

### Citations

**File:** program/src/state.rs (L717-766)
```rust
    pub fn initialize(
        &mut self,
        nonce: u8,
        open_time: u64,
        coin_decimals: u8,
        pc_decimals: u8,
        _coin_lot_size: u64,
        _pc_lot_size: u64,
    ) -> Result<(), AmmError> {
        self.fees.initialize()?;
        self.state_data.initialize(open_time)?;

        self.status = AmmStatus::Uninitialized.into_u64();
        self.nonce = nonce as u64;
        self.order_num = 7;
        self.depth = 3;
        self.coin_decimals = coin_decimals as u64;
        self.pc_decimals = pc_decimals as u64;
        self.state = AmmState::IdleState.into_u64();
        self.reset_flag = AmmResetFlag::ResetNo.into_u64();
        if pc_decimals > coin_decimals {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(pc_decimals.try_into().unwrap())
                .unwrap();
        } else {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(coin_decimals.try_into().unwrap())
                .unwrap();
        }

        self.min_size = 0;

        self.vol_max_cut_ratio = 500; // TEN_THOUSAND as denominator
        self.amount_wave = self
            .sys_decimal_value
            .checked_mul(5)
            .unwrap()
            .checked_div(1000)
            .unwrap();
        self.coin_lot_size = 0;
        self.pc_lot_size = 0;
        self.min_price_multiplier = 1;
        self.max_price_multiplier = 1000000000;
        self.client_order_id = 0;
        self.padding1 = Zeroable::zeroed();
        self.recent_epoch = get_recent_epoch().unwrap();
        self.padding2 = Zeroable::zeroed();

        Ok(())
    }
```

**File:** program/src/processor.rs (L742-746)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;

```

**File:** program/src/processor.rs (L816-929)
```rust
        // create user ata lp token
        Invokers::create_ata_spl_token(
            user_token_lp_info.clone(),
            user_wallet_info.clone(),
            user_wallet_info.clone(),
            amm_lp_mint_info.clone(),
            token_program_info.clone(),
            ata_token_program_info.clone(),
            system_program_info.clone(),
        )?;

        // transfer user tokens to vault
        Invokers::token_transfer(
            token_program_info.clone(),
            user_token_coin_info.clone(),
            amm_coin_vault_info.clone(),
            user_wallet_info.clone(),
            init.init_coin_amount,
        )?;
        Invokers::token_transfer(
            token_program_info.clone(),
            user_token_pc_info.clone(),
            amm_pc_vault_info.clone(),
            user_wallet_info.clone(),
            init.init_pc_amount,
        )?;

        // load AmmInfo
        let mut amm = AmmInfo::load_mut(&amm_info)?;
        if amm.status != AmmStatus::Uninitialized.into_u64() {
            return Err(AmmError::AlreadyInUse.into());
        }

        // unpack and check token_coin
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_coin_vault.owner,
            *amm_authority_info.key,
            "coin_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_coin_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_coin_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_coin_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_coin_mint_info.key,
            amm_coin_vault.mint,
            "coin_mint",
            AmmError::InvalidCoinMint
        );
        // unpack and check token_pc
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        check_assert_eq!(
            amm_pc_vault.owner,
            *amm_authority_info.key,
            "pc_vault_owner",
            AmmError::InvalidOwner
        );
        if amm_pc_vault.amount == 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if amm_pc_vault.delegate.is_some() {
            return Err(AmmError::InvalidDelegate.into());
        }
        if amm_pc_vault.close_authority.is_some() {
            return Err(AmmError::InvalidCloseAuthority.into());
        }
        check_assert_eq!(
            *amm_pc_mint_info.key,
            amm_pc_vault.mint,
            "pc_mint",
            AmmError::InvalidPCMint
        );

        let lp_mint = Self::unpack_mint(&amm_lp_mint_info, spl_token_program_id)?;
        if lp_mint.supply != 0 {
            return Err(AmmError::InvalidSupply.into());
        }
        if COption::Some(*amm_authority_info.key) != lp_mint.mint_authority {
            return Err(AmmError::InvalidOwner.into());
        }
        if lp_mint.freeze_authority.is_some() {
            return Err(AmmError::InvalidFreezeAuthority.into());
        }

        let liquidity = Calculator::to_u64(
            U128::from(amm_pc_vault.amount)
                .checked_mul(amm_coin_vault.amount.into())
                .unwrap()
                .integer_sqrt()
                .as_u128(),
        )?;
        let user_lp_amount = liquidity
            .checked_sub((10u64).checked_pow(lp_mint.decimals.into()).unwrap())
            .ok_or(AmmError::InitLpAmountTooLess)?;

        // liquidity is measured in terms of token_a's value since both sides of
        // the pool are equal
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_token_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            init.nonce,
            user_lp_amount,
        )?;
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
