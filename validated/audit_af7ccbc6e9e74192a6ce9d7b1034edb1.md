### Title
Unprivileged front-running griefing of `SystemInstruction::CreateAccount` via pre-funding the target address ("dust" DoS) - (File: programs/system/src/system_processor.rs)

### Summary
The Stakehouse finding shows that a hard "amount must exactly fit a fixed budget/allow-list" check on a permissionless entry point can be griefed by an unprivileged attacker who tops up the same shared resource with a tiny amount ahead of the legitimate call, causing the legitimate call to revert. The closest reachable analog in Agave is the System Program's `CreateAccount` instruction, whose success criterion is likewise an exact/binary state check (`lamports == 0`) on an account that anyone can pre-fund with an arbitrary — even dust — amount of lamports before the legitimate creator's transaction lands.

### Finding Description
`create_account` in `system_processor.rs` only proceeds if the destination account currently has zero lamports: [1](#0-0) 

```
fn create_account(...) -> Result<(), InstructionError> {
    // if it looks like the `to` account is already in use, bail
    {
        let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
        if to.get_lamports() > 0 {
            ...
            return Err(SystemError::AccountAlreadyInUse.into());
        }
        allocate_and_assign(&mut to, to_address, space, owner, signers, invoke_context)?;
    }
    transfer(...)
}
```

Because the destination address of `CreateAccount` (whether a fresh keypair, a durable-nonce account, a stake account, a vote account, or a `create_with_seed`/PDA-style derived address) is publicly known before the creating transaction lands (it must be present in the transaction to be signed/derived, and for `create_with_seed` addresses it is even fully deterministic from public inputs), **any unprivileged user can transfer as little as 1 lamport to that address before the legitimate `CreateAccount` transaction executes**. Because `System::transfer` has no restriction on the destination account's owner or content, this pre-funding is trivially available to any account holder: [2](#0-1) 

Once `lamports() > 0`, every subsequent `CreateAccount` attempt targeting that exact address permanently fails with `SystemError::AccountAlreadyInUse`, as directly demonstrated by the existing test: [3](#0-2) 

This is the same bug class as the Stakehouse report: a permissionless, externally reachable operation (`Syndicate.stake` / here, System `Transfer`) can mutate a shared state variable (`totalStaked` / here, an account's lamport balance) that a second, unrelated privileged/legitimate flow (`_autoStakeWithSyndicate`'s fixed 12-ETH stake / here, `CreateAccount`'s "must start at exactly 0 lamports" precondition) depends on for success, allowing griefing with a negligible cost outlay by the attacker.

Agave engineers have implicitly acknowledged this exact class of problem: a new, feature-gated instruction `SystemInstruction::CreateAccountAllowPrefund` was added specifically to allow account creation to succeed even when the target address was already pre-funded: [4](#0-3) [5](#0-4) 

However, this mitigation only helps callers who explicitly opt in to the new instruction (once the `create_account_allow_prefund` feature is active) and does not change the behavior of the original, universally used `SystemInstruction::CreateAccount`, which remains the default account-creation path used throughout the ecosystem (stake accounts, nonce accounts, vote accounts, wallets, program-derived accounts via CPI, etc.).

### Impact Explanation
Any unprivileged actor can permanently deny creation of an account at a specific, publicly-known address by transferring a single lamport to it before the intended `CreateAccount` transaction executes. This is a genuine denial-of-service/griefing vector reachable by any funded account with essentially zero cost (one lamport plus a transfer's fee), analogous to the reported `_sETHAmount + totalStaked > 12 ether` griefing pattern. It can be leveraged to block address reservation for wallets, nonce accounts, or any `create_with_seed`-derived account whose address is deterministic and known ahead of time (e.g., before the legitimate owner submits their `CreateAccount` transaction), forcing costly workarounds (choosing a new address/seed) or permanently squatting an address.

### Likelihood Explanation
High reachability: the destination account of `CreateAccount` must be known/signed in advance (or, for `create_with_seed`, is fully derivable from public base/seed/owner), and the attacker only needs an ordinary `Transfer` instruction landing before the target transaction — a standard front-running scenario achievable via mempool observation or address pre-computation, requiring no special privileges, validator role, or contract-specific bug. The behavior is deterministic and already covered by existing unit tests (`test_create_already_in_use`) confirming the check triggers on any lamports > 0, including dust amounts.

### Recommendation
Extend the tolerant "prefunded account" semantics of `create_account_allow_prefund` (i.e., check `data.is_empty() && owner == system_program` rather than `lamports == 0`) to the standard `CreateAccount`/`CreateAccountWithSeed` code paths, or otherwise decouple the "already in use" check from the raw lamport balance so that dust pre-funding by an unrelated third party cannot block legitimate account initialization.

### Proof of Concept
1. Attacker observes (or derives, for `create_with_seed` addresses) the public key `to` that a victim intends to use as the target of a `SystemInstruction::CreateAccount` instruction (e.g., a new stake account, nonce account, or wallet).
2. Attacker submits `SystemInstruction::Transfer { lamports: 1 }` to `to` and it lands first.
3. Victim's `CreateAccount` instruction executes against `to`, hits `to.get_lamports() > 0` in `create_account` (`programs/system/src/system_processor.rs:164`), and fails with `SystemError::AccountAlreadyInUse`, as reproduced by `test_create_already_in_use` (`programs/system/src/system_processor.rs:1014-1041`), which shows a pre-existing single-lamport balance causes `CreateAccount` to be rejected while leaving the funder's lamports untouched.
4. The victim's intended account can never be created at that exact address using `CreateAccount`, permanently denying use of that address unless they switch to a different (unpredictable) keypair or to the feature-gated `CreateAccountAllowPrefund` instruction, which is not the default path used throughout the codebase/ecosystem.

### Citations

**File:** programs/system/src/system_processor.rs (L149-182)
```rust
#[allow(clippy::too_many_arguments)]
fn create_account(
    from_account_index: IndexOfAccount,
    to_account_index: IndexOfAccount,
    to_address: &Address,
    lamports: u64,
    space: u64,
    owner: &Pubkey,
    signers: &HashSet<Pubkey>,
    invoke_context: &InvokeContext,
    instruction_context: &InstructionContext,
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

        allocate_and_assign(&mut to, to_address, space, owner, signers, invoke_context)?;
    }
    transfer(
        from_account_index,
        to_account_index,
        lamports,
        invoke_context,
        instruction_context,
    )
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

**File:** programs/system/src/system_processor.rs (L216-243)
```rust
fn transfer_verified(
    from_account_index: IndexOfAccount,
    to_account_index: IndexOfAccount,
    lamports: u64,
    invoke_context: &InvokeContext,
    instruction_context: &InstructionContext,
) -> Result<(), InstructionError> {
    let mut from = instruction_context.try_borrow_instruction_account(from_account_index)?;
    if !from.get_data().is_empty() {
        ic_msg!(invoke_context, "Transfer: `from` must not carry data");
        return Err(InstructionError::InvalidArgument);
    }
    if lamports > from.get_lamports() {
        ic_msg!(
            invoke_context,
            "Transfer: insufficient lamports {}, need {}",
            from.get_lamports(),
            lamports
        );
        return Err(SystemError::ResultWithNegativeLamports.into());
    }

    from.checked_sub_lamports(lamports)?;
    drop(from);
    let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
    to.checked_add_lamports(lamports)?;
    Ok(())
}
```

**File:** programs/system/src/system_processor.rs (L530-563)
```rust
        SystemInstruction::CreateAccountAllowPrefund {
            lamports,
            space,
            owner,
        } => {
            if !invoke_context
                .get_feature_set()
                .create_account_allow_prefund
            {
                return Err(InstructionError::InvalidInstructionData);
            }
            let from_and_lamports = if lamports > 0 {
                instruction_context.check_number_of_instruction_accounts(2)?;
                Some((1, lamports))
            } else {
                instruction_context.check_number_of_instruction_accounts(1)?;
                None
            };
            let to_address = Address::create(
                instruction_context.get_key_of_instruction_account(0)?,
                None,
                invoke_context,
            )?;
            create_account_allow_prefund(
                0,
                &to_address,
                from_and_lamports,
                space,
                &owner,
                &signers,
                invoke_context,
                &instruction_context,
            )
        }
```

**File:** programs/system/src/system_processor.rs (L1014-1041)
```rust
        // Attempt to create an account that already has lamports
        let owned_account = AccountSharedData::new(1, 0, &Pubkey::default());
        let unchanged_account = owned_account.clone();
        let accounts = process_instruction(
            &bincode::serialize(&SystemInstruction::CreateAccount {
                lamports: 50,
                space: 2,
                owner: new_owner,
            })
            .unwrap(),
            vec![(from, from_account), (owned_key, owned_account)],
            vec![
                AccountMeta {
                    pubkey: from,
                    is_signer: true,
                    is_writable: false,
                },
                AccountMeta {
                    pubkey: owned_key,
                    is_signer: true,
                    is_writable: false,
                },
            ],
            Err(SystemError::AccountAlreadyInUse.into()),
        );
        assert_eq!(accounts[0].lamports(), 100);
        assert_eq!(accounts[1], unchanged_account);
    }
```
