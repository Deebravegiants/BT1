### Title
Deposit instruction never binds the LP-destination account to the signer, letting a delegate-approved attacker redirect a victim's deposit into attacker-owned LP tokens - (File: program/src/processor.rs)

### Summary
`process_deposit` in the Raydium AMM program only checks that `source_owner_info.is_signer` is true; it never verifies that the token accounts being debited (`user_source_coin_info`, `user_source_pc_info`) or the LP account being credited (`user_dest_lp_info`) are actually owned by the signer. Just like the `PledgeManager::pledge` bug where the contract never enforced `msg.sender == data.signer`, this instruction never enforces that the account which is credited with new LP tokens belongs to the same party whose coin/pc tokens are being spent.

### Finding Description
`process_deposit` reads the accounts and only checks `source_owner_info.is_signer`: [1](#0-0) 

The actual debit of the user's coin/pc token accounts is performed with `Invokers::token_transfer`, passing `source_owner_info` as the SPL Token `authority`: [2](#0-1) 

Whether this succeeds is entirely delegated to the SPL Token program's own authority check, which accepts either the token account's actual `owner` **or any approved SPL Token delegate** as a valid signer for `Transfer`. The AMM program itself performs no additional binding between `source_owner_info` and the actual `owner` field of `user_source_coin_info` / `user_source_pc_info` (contrast this with `process_withdraw`, which does check `user_source_lp.owner != *source_lp_owner_info.key`): [3](#0-2) 

Critically, after the debit, the newly minted LP tokens are minted straight to whatever account is passed as `user_dest_lp_info`, again with **no check at all** that this account's owner matches `source_owner_info`: [4](#0-3) 

Because `user_dest_lp_info`, `user_source_coin_info`, and `user_source_pc_info` are all attacker-chosen accounts in a single submitted transaction, and the only required signer is `source_owner_info`, an attacker who has been granted an SPL Token `Approve` delegation on a victim's coin/pc accounts (a common leftover-approval scenario, exactly analogous to the ERC-20 `approve` case in the report) can:
1. Sign the `Deposit` instruction as the delegate (`source_owner_info` = attacker's own key, which the SPL Token program accepts as a valid delegate-authority for the victim's `user_source_coin_info`/`user_source_pc_info`).
2. Supply an LP token account owned by the **attacker** as `user_dest_lp_info`.

The program debits the victim's coin/pc tokens into the pool vaults and mints the resulting LP shares to the attacker's account — the victim's tokens are spent, but the attacker receives the LP position instead of the victim.

### Impact Explanation
This results in concrete theft of user funds: a victim's coin/pc tokens are pulled into the pool while the attacker walks away with the LP shares representing that value. This is a direct, reachable state-modifying effect from a single unprivileged instruction (`Deposit`) with attacker-controlled accounts, matching the "theft of user funds" criterion.

### Likelihood Explanation
Exploitability requires the victim to have left an SPL Token delegate approval outstanding on their coin and/or pc token accounts (e.g., to a bot, aggregator, or previously-used frontend) — directly analogous to the "open token approval" precondition in the original report. Given how common lingering token delegations are in DeFi tooling, this is a realistic and not merely theoretical precondition.

### Recommendation
In `process_deposit` (and equivalently review `process_withdraw`'s existing but comparable pattern), explicitly verify account ownership bindings rather than relying solely on the SPL Token program's authority/delegate check:
- Require `user_source_coin.owner == *source_owner_info.key` and `user_source_pc.owner == *source_owner_info.key`.
- Require `user_dest_lp.owner == *source_owner_info.key` (or otherwise explicitly document/allow third-party destinations only via a dedicated, clearly-labeled parameter, not implicitly).

### Proof of Concept
1. Victim `V` approves attacker `A` as an SPL Token delegate with sufficient allowance on `V`'s coin and pc token accounts (e.g., a common integration pattern).
2. `A` submits a `Deposit` instruction:
   - `source_owner_info` = `A` (signer, valid delegate on `V`'s accounts)
   - `user_source_coin_info` / `user_source_pc_info` = `V`'s coin/pc token accounts
   - `user_dest_lp_info` = `A`'s own LP token account
3. `process_deposit` passes signer checks (`A.is_signer == true`), the SPL Token CPI succeeds because `A` is a valid delegate on `V`'s source accounts, and the LP mint-to at [5](#0-4) 
credits `A`'s account with `mint_lp_amount` LP tokens.
4. Result: `V`'s tokens are deposited into the pool, but `A` receives the LP shares — a direct theft of `V`'s deposited value.

### Citations

**File:** program/src/processor.rs (L1097-1099)
```rust
        if !source_owner_info.is_signer {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/processor.rs (L1327-1340)
```rust
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_coin_info.clone(),
            amm_coin_vault_info.clone(),
            source_owner_info.clone(),
            deduct_coin_amount,
        )?;
        Invokers::token_transfer(
            token_program_info.clone(),
            user_source_pc_info.clone(),
            amm_pc_vault_info.clone(),
            source_owner_info.clone(),
            deduct_pc_amount,
        )?;
```

**File:** program/src/processor.rs (L1341-1350)
```rust
        Invokers::token_mint_to(
            token_program_info.clone(),
            amm_lp_mint_info.clone(),
            user_dest_lp_info.clone(),
            amm_authority_info.clone(),
            AUTHORITY_AMM,
            amm.nonce as u8,
            mint_lp_amount,
        )?;
        amm.lp_amount = amm.lp_amount.checked_add(mint_lp_amount).unwrap();
```

**File:** program/src/processor.rs (L1705-1709)
```rust
        let user_source_lp =
            Self::unpack_token_account(&user_source_lp_info, spl_token_program_id)?;
        if user_source_lp.owner != *source_lp_owner_info.key {
            return Err(AmmError::InvalidOwner.into());
        }
```
