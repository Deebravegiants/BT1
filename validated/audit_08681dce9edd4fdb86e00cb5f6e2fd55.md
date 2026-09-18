### Title
Permissionless `Initialize2` lets an attacker front-run pool creation for a given market and set an arbitrary initial price - ([File: program/src/processor.rs])

### Summary
`process_initialize2` has no authorization requirement beyond "some signer paid for it" — any wallet can call `Initialize2` supplying an arbitrary `market_info` account and arbitrary `init_pc_amount`/`init_coin_amount`. Because the AMM pool address, vaults, LP mint and target-orders accounts are all derived deterministically from the `market_info` pubkey, this lets an attacker pre-empt ("front-run") the intended pool creator for that market and seed the pool with a skewed initial price of their own choosing.

### Finding Description
`process_initialize2` only checks `user_wallet_info.is_signer` [1](#0-0) , the config PDA, the AMM authority PDA, and the create-fee-destination address [2](#0-1) . There is no check that the caller is a particular "intended" pool creator, nor any binding between the `market_info` account and a real, immutable price oracle — the comment explicitly states `market_info` is "Just a seed for AMM account. Can be any account." [3](#0-2) .

The AMM pool account, target-orders account, LP mint, and coin/pc vaults are all created via `generate_amm_associated_account`/`generate_amm_associated_spl_mint`/`generate_amm_associated_spl_token`, which derive their addresses deterministically from `[program_id, market_account.key, associated_seed]` [4](#0-3) [5](#0-4) . Since these addresses depend only on the public `market_info` pubkey (not on the caller's identity), an attacker who observes (or predicts) that a specific market account will be used to create a pool can submit their own `Initialize2` transaction first, using the same `market_info` but supplying their own `init_pc_amount`/`init_coin_amount` in whatever ratio they want.

The initial liquidity/LP amount is computed purely from the deposited amounts: `liquidity = sqrt(pc_amount * coin_amount)`, and `user_lp_amount = liquidity - 10^lp_decimals` [6](#0-5) . The only floor preventing a near-zero/degenerate pool is that `liquidity` must exceed `10^decimals`, but there is no check that the price ratio matches any legitimate/expected value. The pool's `status`, `coin_vault`, `pc_vault`, `lp_mint` and `target_orders` are then written into `AmmInfo` and the account moves from `Uninitialized` to `WaitingTrade`/`SwapOnly` [7](#0-6) . Once initialized, `amm.status != Uninitialized` causes any subsequent legitimate `Initialize2` attempt for the same market to fail with `AlreadyInUse` [8](#0-7) , permanently locking in the attacker's chosen price for that market/pool address.

### Impact Explanation
An attacker can permanently hijack the pool for a targeted market with a self-chosen initial price ratio, denying the legitimate deployer the ability to create the intended pool (the deterministic address is already `AlreadyInUse`), and forcing any subsequent depositors/swappers to interact with a pool whose price is arbitrarily skewed by the attacker. Later liquidity providers depositing based on the current (attacker-set) ratio will receive LP tokens proportional to that distorted ratio, and swappers trading against the distorted price can suffer value loss to the attacker via arbitrage, constituting a realistic path to loss of user/LP funds. This matches the report's underlying bug class ("lack of access control on initializer" front-running) as applied to the deterministic, market-account-derived Solana PDA/account creation instead of an EVM proxy `initialize()`.

### Likelihood Explanation
Medium: pool creation is intentionally permissionless in Raydium AMM by design (anyone should be able to create a pool for a market), which is normal DEX behavior and mitigates severity somewhat. However, the complete absence of any check binding `market_info` to caller intent, combined with deterministic address derivation purely from the public `market_info` key, means any observer of a pending "create pool" transaction (or anyone who simply predicts which market will be paired) can front-run it in a single transaction with attacker-chosen `init_pc_amount`/`init_coin_amount`, requiring only that they hold enough of both tokens to clear the `liquidity > 10^decimals` floor.

### Recommendation
Consider requiring the pool creator to specify/commit to an expected price band, or emit checks tying the vault mints/market to an authoritative price reference before minting LP tokens, or add commit-reveal / minimum-liquidity-lock mechanisms so that a front-runner cannot dictate the permanent initial price for a market with only nominal committed capital. At minimum, document that `Initialize2` callers must independently verify their pool address is not already claimed with the wrong ratio before depositing further liquidity, and consider allowing pool re-initialization/migration paths for markets initialized with adversarial ratios.

### Proof of Concept
1. Victim decides to create an AMM pool for market `M` pairing tokens `A`/`B` at a fair ratio (e.g., matching current market price).
2. Victim broadcasts an `Initialize2` transaction referencing `market_info = M`.
3. Attacker observes the pending transaction (or independently decides to target `M`) and submits their own `Initialize2` transaction for the same `market_info = M`, but with `init_coin_amount`/`init_pc_amount` set to an extreme ratio (still exceeding the `10^decimals` liquidity floor) using their own token accounts.
4. Because `process_initialize2` performs no check tying the caller to a specific intended deployer, and the AMM/vault/LP-mint addresses are deterministically derived only from `market_info`, the attacker's transaction lands first (or is simply submitted before the victim's), creating the pool at the deterministic address with the attacker's skewed price and minting themselves `user_lp_amount = sqrt(x*y) - 10^decimals` LP tokens [9](#0-8) .
5. The victim's original `Initialize2` transaction now fails with `AmmError::AlreadyInUse` [8](#0-7) , and all subsequent deposits/swaps against market `M` operate against the attacker-controlled skewed price.

### Citations

**File:** program/src/processor.rs (L386-404)
```rust
    fn generate_amm_associated_spl_mint<'a, 'b: 'a>(
        program_id: &Pubkey,
        spl_token_program_id: &Pubkey,
        market_account: &'a AccountInfo<'b>,
        associated_token_account: &'a AccountInfo<'b>,
        user_wallet_account: &'a AccountInfo<'b>,
        system_program_account: &'a AccountInfo<'b>,
        rent_sysvar_account: &'a AccountInfo<'b>,
        spl_token_program_account: &'a AccountInfo<'b>,
        associated_owner_account: &'a AccountInfo<'b>,
        associated_seed: &[u8],
        mint_decimals: u8,
    ) -> ProgramResult {
        let (associated_token_address, bump_seed) = get_associated_address_and_bump_seed(
            program_id,
            &market_account.key,
            associated_seed,
            program_id,
        );
```

**File:** program/src/processor.rs (L478-494)
```rust
    fn generate_amm_associated_account<'a, 'b: 'a>(
        program_id: &Pubkey,
        assign_to: &Pubkey,
        market_account: &'a AccountInfo<'b>,
        associated_token_account: &'a AccountInfo<'b>,
        user_wallet_account: &'a AccountInfo<'b>,
        system_program_account: &'a AccountInfo<'b>,
        _rent_sysvar_account: &'a AccountInfo<'b>,
        associated_seed: &[u8],
        data_size: usize,
    ) -> ProgramResult {
        let (associated_token_address, bump_seed) = get_associated_address_and_bump_seed(
            &program_id,
            &market_account.key,
            associated_seed,
            program_id,
        );
```

**File:** program/src/processor.rs (L592-594)
```rust
            // Just a seed for AMM account.
            // Can be any account.
            let market_info = next_account_info(account_info_iter)?;
```

**File:** program/src/processor.rs (L675-714)
```rust
        let (pda, _) = Pubkey::find_program_address(&[&AMM_CONFIG_SEED], program_id);
        if pda != *amm_config_info.key || amm_config_info.owner != program_id {
            return Err(AmmError::InvalidConfigAccount.into());
        }

        if *amm_coin_mint_info.key == *amm_pc_mint_info.key {
            return Err(AmmError::InvalidCoinMint.into());
        }

        msg!(arrform!(LOG_SIZE, "initialize2: {:?}", init).as_str());
        if !user_wallet_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
        check_assert_eq!(
            *token_program_info.key,
            spl_token::id(),
            "spl_token_program",
            AmmError::InvalidSplTokenProgram
        );
        let spl_token_program_id = token_program_info.key;
        check_assert_eq!(
            *ata_token_program_info.key,
            spl_associated_token_account::id(),
            "spl_associated_token_account",
            AmmError::InvalidSplTokenProgram
        );
        check_assert_eq!(
            *system_program_info.key,
            solana_system_interface::program::id(),
            "sys_program",
            AmmError::InvalidSysProgramAddress
        );
        let (expect_amm_authority, expect_nonce) =
            Pubkey::find_program_address(&[&AUTHORITY_AMM], program_id);
        if *amm_authority_info.key != expect_amm_authority || init.nonce != expect_nonce {
            return Err(AmmError::InvalidProgramAddress.into());
        }
        if *create_fee_destination_info.key != config_feature::create_pool_fee_address::id() {
            return Err(AmmError::InvalidFee.into());
        }
```

**File:** program/src/processor.rs (L844-847)
```rust
        let mut amm = AmmInfo::load_mut(&amm_info)?;
        if amm.status != AmmStatus::Uninitialized.into_u64() {
            return Err(AmmError::AlreadyInUse.into());
        }
```

**File:** program/src/processor.rs (L908-929)
```rust
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

**File:** program/src/processor.rs (L967-985)
```rust
        amm.coin_vault = *amm_coin_vault_info.key;
        amm.pc_vault = *amm_pc_vault_info.key;
        amm.coin_vault_mint = *amm_coin_mint_info.key;
        amm.pc_vault_mint = *amm_pc_mint_info.key;
        amm.lp_mint = *amm_lp_mint_info.key;
        amm.open_orders = Pubkey::default();
        amm.market = *market_info.key;
        amm.market_program = Pubkey::default();
        amm.target_orders = *amm_target_orders_info.key;
        amm.amm_owner = config_feature::amm_owner::ID;
        amm.lp_amount = liquidity;
        amm.status = if init.open_time > (Clock::get()?.unix_timestamp as u64) {
            AmmStatus::WaitingTrade.into_u64()
        } else {
            AmmStatus::SwapOnly.into_u64()
        };
        amm.reset_flag = AmmResetFlag::ResetYes.into_u64();

        Ok(())
```
