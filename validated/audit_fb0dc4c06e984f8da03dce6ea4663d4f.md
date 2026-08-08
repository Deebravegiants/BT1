## Analysis

The reported Code4rena issue is a "pre-fund a not-yet-existing deterministic address to permanently DoS creation" bug class. The Agave analog exists in the native System Program's account-creation logic.

### Title
Unprivileged pre-funding of a deterministic `CreateAccount`/`CreateAccountWithSeed` target address causes permanent instruction failure (`AccountAlreadyInUse`) — (File: `programs/system/src/system_processor.rs`)

### Summary
`system_processor::create_account`, which backs both `SystemInstruction::CreateAccount` and `SystemInstruction::CreateAccountWithSeed`, rejects account creation whenever the target account already holds any lamports (`to.get_lamports() > 0`), regardless of who put those lamports there. [1](#0-0) 
Because target addresses for `CreateAccountWithSeed` are fully deterministic (`Pubkey::create_with_seed(base, seed, owner)`, derivable off-chain by anyone who knows the public `base`/`seed`/`owner`), and even plain `CreateAccount` targets are frequently publicly known ahead of time (e.g. CLI flows compute the address before submitting the creating transaction), any unprivileged actor can front-run the legitimate creation transaction with a trivial 1-lamport `SystemInstruction::Transfer` to that address. [2](#0-1) [3](#0-2) 

### Finding Description
`create_account` performs a single check before allocating/assigning and transferring lamports:

```rust
let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
if to.get_lamports() > 0 {
    ...
    return Err(SystemError::AccountAlreadyInUse.into());
}
``` [4](#0-3) 

This is the exact same "pool/account already exists" check pattern described in the LamboFactory report (`getPair[token0][token1] == address(0)`). Since Solana account addresses used with `create_with_seed` are computed purely from public inputs (`base`, `seed` string, `owner` program id), and plain keypair-based `to` addresses are also often published/known ahead of submission (needed to co-sign the transaction), an attacker can:
1. Observe or derive the target address before the legitimate `CreateAccount`/`CreateAccountWithSeed` transaction lands.
2. Send it 1 lamport via a plain `SystemInstruction::Transfer` (any unprivileged wallet can do this).
3. Cause every future `CreateAccount`/`CreateAccountWithSeed` attempt at that exact address to permanently fail with `SystemError::AccountAlreadyInUse`, since lamports cannot be removed from an account without ownership/signing rights already held by the intended new owner.

Test coverage confirms this is the intended (but weaponizable) behavior: `test_create_already_in_use` explicitly validates that "Attempt to create an account that already has lamports" fails. [5](#0-4) 

Notably, Agave has already recognized this exact griefing vector and introduced a mitigation: `SystemInstruction::CreateAccountAllowPrefund`, which explicitly skips the zero-lamports check and allows creation over a pre-funded account. [6](#0-5) 
However this is an opt-in, feature-gated instruction (`invoke_context.get_feature_set().create_account_allow_prefund`) that must be explicitly used by callers. [7](#0-6) 
The original `CreateAccount`/`CreateAccountWithSeed` paths — used pervasively by essentially all existing on-chain programs and CLI tooling (e.g. nonce account creation with seed) — remain fully exposed. [8](#0-7) 

### Impact Explanation
Any unprivileged user can permanently deny creation of a specific, targeted account address for any protocol relying on `CreateAccount`/`CreateAccountWithSeed` with a predictable/derivable address (escrow accounts, per-user PDAs created via `create_with_seed`, nonce accounts, associated-account-style flows, etc.). This is a griefing/DoS vector, not a fund-theft vector, but it is unrecoverable for the specific targeted address (the account can never be "created" there again through the normal instruction, matching the "permanent DoS" impact class of the original report).

### Likelihood Explanation
Trivial to execute: the attacker needs only the ability to submit a standard `SystemInstruction::Transfer` for 1 lamport to a known/derivable address before the victim's creation transaction is processed — no special privileges, and address derivation for `CreateAccountWithSeed` is a pure public-input function that can be computed by anyone.

### Recommendation
Extend the pre-funding tolerance from the opt-in `CreateAccountAllowPrefund` instruction to the standard `CreateAccount`/`CreateAccountWithSeed` paths (or make it the default/fallback behavior of `create_account`), rather than requiring every caller to explicitly adopt a separate, feature-gated instruction. At minimum, protocols/tools that build deterministic-address account creation on top of `CreateAccount`/`CreateAccountWithSeed` should be documented as vulnerable and steered toward `CreateAccountAllowPrefund`.

### Proof of Concept
1. Attacker computes `to = Pubkey::create_with_seed(&base, seed, &owner)` for a target protocol account that will later be created via `SystemInstruction::CreateAccountWithSeed` (or observes the plain address for `CreateAccount` flows, e.g. as done client-side in `cli/src/nonce.rs`).
2. Attacker submits `SystemInstruction::Transfer { lamports: 1 }` to `to`.
3. Victim protocol later submits `SystemInstruction::CreateAccountWithSeed { base, seed, lamports, space, owner }` targeting `to`; `create_account` sees `to.get_lamports() > 0` and returns `SystemError::AccountAlreadyInUse`, exactly as exercised by `test_create_already_in_use`. [5](#0-4) 
4. The victim protocol cannot ever complete creation at that specific derived address via the standard instruction, permanently blocking that address's intended use.

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

**File:** programs/system/src/system_processor.rs (L354-378)
```rust
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

**File:** programs/system/src/system_processor.rs (L530-547)
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

**File:** cli/src/nonce.rs (L452-467)
```rust
pub async fn process_create_nonce_account(
    rpc_client: &RpcClient,
    config: &CliConfig<'_>,
    nonce_account: SignerIndex,
    seed: Option<String>,
    nonce_authority: Option<Pubkey>,
    memo: Option<&String>,
    mut amount: SpendAmount,
    compute_unit_price: Option<u64>,
) -> ProcessResult {
    let nonce_account_pubkey = config.signers[nonce_account].pubkey();
    let nonce_account_address = if let Some(ref seed) = seed {
        Pubkey::create_with_seed(&nonce_account_pubkey, seed, &system_program::id())?
    } else {
        nonce_account_pubkey
    };
```
