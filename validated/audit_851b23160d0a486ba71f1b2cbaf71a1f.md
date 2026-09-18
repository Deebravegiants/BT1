Confirmed: `process_initialize2` checks `delegate.is_some()`, `close_authority.is_some()`, and `mint.freeze_authority.is_some()` only for the **LP mint** and vault token accounts — it never checks whether `coin_mint`/`pc_mint` themselves carry a `freeze_authority`. This is the closest structural analog to the Illuminate report: the protocol validates some but not all "can this asset be externally paused/frozen by a third party" conditions before minting shares/accepting deposits, leaving other pool participants exposed to a party who can unilaterally freeze/void the asset later.

### Title
Unchecked `freeze_authority` on pool `coin_mint`/`pc_mint` allows permanent freezing of all LPs' pooled funds - (File: `program/src/processor.rs`)

### Summary
`Processor::process_initialize2` validates that the LP mint has no `freeze_authority` and that the coin/pc vault token accounts have no `delegate` or `close_authority`, but it never checks whether the underlying `coin_mint` or `pc_mint` themselves have a `freeze_authority` set. Any unprivileged pool creator can therefore create a pool using a token whose mint retains a freeze authority (controlled by the creator or a colluding party), later deposit/attract other users' liquidity, and then freeze the pool's vault token account at will, permanently locking the funds of all other depositors in that pool.

### Finding Description
In `process_initialize2` (`program/src/processor.rs:742-906`), the mints are unpacked via `Self::unpack_mint` at lines 743-745, but the only freeze-authority check performed anywhere in this function is on the newly created `lp_mint` at lines 904-906: [1](#0-0) 

No equivalent check exists for `coin_mint` or `pc_mint`: [2](#0-1) 

The vault accounts (`amm_coin_vault_info`, `amm_pc_vault_info`) are checked for `delegate` and `close_authority` but not for whether the *mint* backing them has an active `freeze_authority`: [3](#0-2) 

Because SPL Token mints with an active `freeze_authority` allow that authority to call `FreezeAccount` on any token account of that mint at any time — including the AMM's own `coin_vault`/`pc_vault` PDAs — a pool creator (or any party who controls the mint's freeze authority) can:
1. Create a pool via `Initialize2` using a mint they control the freeze authority of.
2. Wait for other, unrelated users to deposit liquidity via `Deposit` (`process_deposit`, `program/src/processor.rs:989+`) or accumulate swap volume.
3. Freeze the `coin_vault` or `pc_vault` token account, which blocks all further `SPL Token::Transfer` calls out of that vault.

Once frozen, `process_withdraw` and both swap paths (`process_swap_base_in`/`process_swap_base_out`) will fail at the `Invokers::token_transfer*` CPI calls in `program/src/invokers.rs`, because the underlying `spl_token::instruction::transfer` will be rejected by the token program for a frozen account. This permanently locks the pooled funds of every LP in that pool, with no code path in `AmmStatus`/`SetParams` able to un-freeze a token account controlled by an external mint authority — this is an entirely off-chain, third-party privileged action the program never accounts for.

### Impact Explanation
This directly matches the accepted impact category for the external report: permanent freezing of user/LP funds caused by the protocol never validating that the accepted asset cannot later be unilaterally paused/frozen by an outside party. Every other liquidity provider who deposits into a pool created with such a mint has no recourse — their coin/pc share becomes permanently locked once the freeze authority acts, and because the freeze is external to the Raydium program (an SPL Token Program admin action, not a program instruction), the AMM's own `AmmStatus`/pause mechanism cannot mitigate it.

### Likelihood Explanation
Likelihood is high in the sense that it requires no protocol privilege at all — anyone creating a permissionless SPL token can retain the freeze authority and then create a Raydium pool with it via a single `Initialize2` transaction using attacker-chosen mint accounts, exactly as permitted by the instruction's account list. The only precondition is that other users later deposit or hold LP positions in that specific pool, which is a normal expected usage pattern for any newly created pool listed with real-looking liquidity.

### Recommendation
In `process_initialize2`, add an explicit check (mirroring the existing `lp_mint.freeze_authority.is_some()` check) that rejects pool creation if `coin_mint.freeze_authority.is_some()` or `pc_mint.freeze_authority.is_some()`, e.g., immediately after unpacking `coin_mint`/`pc_mint` at line 743-745:
```rust
if coin_mint.freeze_authority.is_some() || pc_mint.freeze_authority.is_some() {
    return Err(AmmError::InvalidFreezeAuthority.into());
}
```

### Proof of Concept
1. Attacker creates SPL Token mint `M` retaining `freeze_authority = attacker_key` (standard `spl_token::instruction::initialize_mint`, no program modification needed).
2. Attacker calls `Initialize2` (`program/src/instruction.rs:663-729`) using `M` as `amm_coin_mint` (or `amm_pc_mint`) paired with a legitimate token (e.g., USDC) as the other side — this succeeds because `process_initialize2` never inspects `coin_mint.freeze_authority`/`pc_mint.freeze_authority` (`program/src/processor.rs:742-906`).
3. Legitimate LPs deposit via `Deposit` (`program/src/processor.rs:989` onward), growing `amm.coin_vault`/`amm.pc_vault` balances and `amm.lp_amount`.
4. Attacker calls SPL Token Program's `FreezeAccount` on the pool's `coin_vault` (or `pc_vault`) token account using their retained `freeze_authority`.
5. All subsequent `Withdraw` and `SwapBaseIn`/`SwapBaseOut`/`SwapBaseInV2`/`SwapBaseOutV2` calls fail at the `Invokers::token_transfer*` CPI step because the frozen vault rejects transfers, permanently locking every other LP's deposited funds in the pool with no recovery path through the AMM program.

### Citations

**File:** program/src/processor.rs (L742-745)
```rust
        // unpack and check coin_mint
        let coin_mint = Self::unpack_mint(&amm_coin_mint_info, spl_token_program_id)?;
        // unpack and check pc_mint
        let pc_mint = Self::unpack_mint(&amm_pc_mint_info, spl_token_program_id)?;
```

**File:** program/src/processor.rs (L858-895)
```rust
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
```

**File:** program/src/processor.rs (L897-906)
```rust
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
```
