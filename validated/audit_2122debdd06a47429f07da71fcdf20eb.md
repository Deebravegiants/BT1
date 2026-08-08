## Title
Unprivileged dust-lamport prefunding permanently blocks `SystemInstruction::CreateAccount` for a target address — ([File: programs/system/src/system_processor.rs])

## Summary
The NFTX finding is a griefing/DoS pattern: an unprivileged actor sends a small, non-zero balance to an address before the legitimate "create/mint" flow runs, causing a strict equality/zero-balance check baked into shared infrastructure to fail forever for that address, permanently denying service to everyone who needs that address. The same bug class exists in Agave's System Program: `create_account` (used for `SystemInstruction::CreateAccount` / `CreateAccountWithSeed`) rejects the operation outright if the destination already holds `lamports > 0`.

## Finding Description
`create_account` in `programs/system/src/system_processor.rs` enforces:
```
if to.get_lamports() > 0 {
    ic_msg!(invoke_context, "Create Account: account {:?} already in use", to_address);
    return Err(SystemError::AccountAlreadyInUse.into());
}
``` [1](#0-0) 

This check is reached by `SystemInstruction::CreateAccount` and `SystemInstruction::CreateAccountWithSeed`, dispatched directly from the System Program's `declare_process_instruction!` entrypoint with no privileged/role gating — any signer of a transfer instruction can send lamports to any known/derivable address before its owner attempts to create it there. [2](#0-1) 

Because Solana account addresses for PDAs, `CreateAccountWithSeed` derivations, and other deterministic targets (nonce accounts, stake accounts, program buffer accounts, associated accounts built by higher-level protocols, etc.) are computable in advance by anyone, an attacker can front-run legitimate account creation by transferring as little as 1 lamport to the target address. Once lamports are non-zero, every subsequent `CreateAccount`/`CreateAccountWithSeed` attempt at that exact address fails with `AccountAlreadyInUse`, permanently — there is no way to "un-fund" an account, and the legitimate protocol/user has no recourse other than deriving a brand-new address (which may not be possible if the address is a required PDA seed).

Notably, the codebase itself has already recognized this exact bug class: it recently introduced `SystemInstruction::CreateAccountAllowPrefund`, whose processor `create_account_allow_prefund` explicitly skips the zero-lamport check ("Create a new account without checking for 0 lamports. All other checks remain. Intended for use where account has already had rent paid in whole or in part before creation."). [3](#0-2) 
This is a targeted mitigation for callers that opt into it, but the original `CreateAccount`/`CreateAccountWithSeed` paths — still the default and most widely used across the ecosystem (CPI'd by countless on-chain programs and CLI tooling) — remain vulnerable to the griefing pattern for any caller that has not migrated to the new instruction, or cannot (because address derivation determinism is required and dust-funding happens before the transaction is even built).

## Impact Explanation
This is a genuine unprivileged-user-reachable denial-of-service in the SVM execution path: any address that a protocol intends to `CreateAccount`/`CreateAccountWithSeed` into can be permanently blocked from being created by a trivial 1-lamport transfer from any account. This directly mirrors the "[H-03]" NFTX pattern — value/functionality is permanently locked for legitimate users because of a strict, griefable pre-condition check reachable by anyone. Any downstream protocol that derives a deterministic address (PDA/seed-based) and relies on vanilla `CreateAccount` to initialize it (rather than the newer `CreateAccountAllowPrefund` or an idempotent "create-if-not-exists" pattern) can be permanently denied service for that specific account/user, causing stuck funds, unusable stake/nonce/vote accounts, or blocked program initialization flows.

## Likelihood Explanation
High likelihood of reachability: `Transfer`/`CreateAccount` are core, always-enabled System Program instructions with no feature gate protecting the vulnerable code path, and computing a target address ahead of time (via `Pubkey::create_with_seed` or PDA derivation) is trivial and public. The only "mitigation" (`CreateAccountAllowPrefund`) is opt-in and feature-gated, so the vast majority of existing account-creation call sites (on-chain programs and clients) remain exposed. Exploitation requires only a single, cheap `Transfer` instruction from an attacker-controlled account.

## Recommendation
Where feasible, migrate account-creation flows that must land at a deterministic address to `SystemInstruction::CreateAccountAllowPrefund` (already implemented in `create_account_allow_prefund`), which tolerates a pre-funded balance while preserving all other safety checks (data emptiness, owner assignment, signer checks). [4](#0-3) 
For the legacy `CreateAccount`/`CreateAccountWithSeed` instructions, consider documenting/deprecating the strict `lamports > 0` rejection in favor of the "allow prefund" semantics by default in future protocol/client tooling guidance, since the strict check offers no meaningful security benefit (ownership/data-emptiness checks in `allocate_and_assign` already prevent hijacking an account that has been assigned or has data) while creating a griefing vector identical in spirit to the reported NFTX vulnerability.

## Proof of Concept
1. Compute the deterministic destination address a protocol/user will use for `CreateAccount` (e.g., a PDA-equivalent address derived via `Pubkey::create_with_seed`, or any known target pubkey intended for future account creation).
2. Submit a `SystemInstruction::Transfer` of 1 lamport from any funded account to that destination address before the legitimate creation transaction lands. [5](#0-4) 
3. When the legitimate party submits `SystemInstruction::CreateAccount` (or `CreateAccountWithSeed`) targeting that address, `create_account` observes `to.get_lamports() > 0` and returns `SystemError::AccountAlreadyInUse`, permanently blocking creation at that address. [1](#0-0) 
4. Because the address was deterministically derived, the legitimate party cannot simply pick a new address without breaking whatever seed/PDA logic the higher-level protocol relies on, resulting in a permanent denial of service for that specific account — directly analogous to the vault-locking griefing described in the NFTX report.

### Citations

**File:** programs/system/src/system_processor.rs (L160-171)
```rust
) -> Result<(), InstructionError> {
    // if it looks like the `to` account is already in use, bail
    {
        let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
        if to.get_lamports() > 0 {
            ic_msg!(
                invoke_context,
                "Create Account: account {:?} already in use",
                to_address
            );
            return Err(SystemError::AccountAlreadyInUse.into());
        }
```

**File:** programs/system/src/system_processor.rs (L184-214)
```rust
/// Create a new account without checking for 0 lamports. All other checks remain.
/// Intended for use where account has already had rent paid in whole or in part
/// before creation.
#[allow(clippy::too_many_arguments)]
fn create_account_allow_prefund(
    to_account_index: IndexOfAccount,
    to_address: &Address,
    from_and_lamports: Option<(IndexOfAccount, u64)>,
    space: u64,
    owner: &Pubkey,
    signers: &HashSet<Pubkey>,
    invoke_context: &InvokeContext,
    instruction_context: &InstructionContext,
) -> Result<(), InstructionError> {
    {
        let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
        allocate_and_assign(&mut to, to_address, space, owner, signers, invoke_context)?;
    }
    if let Some((from_account_index, lamports)) = from_and_lamports
        && lamports > 0
    {
        transfer(
            from_account_index,
            to_account_index,
            lamports,
            invoke_context,
            instruction_context,
        )?;
    }
    Ok(())
}
```

**File:** programs/system/src/system_processor.rs (L330-378)
```rust
        SystemInstruction::CreateAccount {
            lamports,
            space,
            owner,
        } => {
            instruction_context.check_number_of_instruction_accounts(2)?;
            let to_address = Address::create(
                instruction_context.get_key_of_instruction_account(1)?,
                None,
                invoke_context,
            )?;
            create_account(
                0,
                1,
                &to_address,
                lamports,
                space,
                &owner,
                &signers,
                invoke_context,
                &instruction_context,
            )
        }

        SystemInstruction::CreateAccountWithSeed {
            base,
            seed,
            lamports,
            space,
            owner,
        } => {
            instruction_context.check_number_of_instruction_accounts(2)?;
            let to_address = Address::create(
                instruction_context.get_key_of_instruction_account(1)?,
                Some((&base, &seed, &owner)),
                invoke_context,
            )?;
            create_account(
                0,
                1,
                &to_address,
                lamports,
                space,
                &owner,
                &signers,
                invoke_context,
                &instruction_context,
            )
        }
```

**File:** programs/system/src/system_processor.rs (L389-392)
```rust
        SystemInstruction::Transfer { lamports } => {
            instruction_context.check_number_of_instruction_accounts(2)?;
            transfer(0, 1, lamports, invoke_context, &instruction_context)
        }
```
