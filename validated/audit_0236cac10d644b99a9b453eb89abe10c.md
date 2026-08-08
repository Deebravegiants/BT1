### Title
Missing signer/authorization check on `InitializeNonceAccount` allows front-running of nonce authority assignment - (File: `programs/system/src/system_instruction.rs`)

### Summary
The `InitializeNonceAccount` system instruction sets the durable-nonce `authority` field on an account without requiring any signature from the account itself, its creator, or any privileged party. This mirrors the reported `createERC721` bug class: a resource is created in one step (owned by a generic/system entity) and a second step assigns real "ownership"/authority — but nothing prevents an unrelated third party from performing that second step first, seizing control of the resource before the rightful owner's transaction lands.

### Finding Description
`initialize_nonce_account` only verifies that the target account is writable and currently `State::Uninitialized`; it performs no signer check at all before writing the caller-supplied `authorized` pubkey into the account state: [1](#0-0) 

The dispatch site in the system program entrypoint likewise performs no signer verification for this instruction — it only checks the number of accounts and fetches the `RecentBlockhashes`/`Rent` sysvars before calling straight into `initialize_nonce_account`: [2](#0-1) 

Contrast this with `assign`/`create_account`, where the target account's `Address` must be a transaction signer before its `owner` can be changed: [3](#0-2) 

Because `InitializeNonceAccount` requires no signature at all, any transaction that references the (public) nonce-account pubkey as account index 0 can initialize it, regardless of who created or funded it. If a nonce account is created (e.g., via `CreateAccount`/`CreateAccountWithSeed`/`CreateAccountAllowPrefund`, which do require signer(s) on the *to* address) in a transaction separate from the `InitializeNonceAccount` call that sets the authority, there is a window where the account is system-owned, funded, and `Uninitialized` — exactly the "factory still owns it" state described in the ERC721 report. An attacker can race this window and submit `InitializeNonceAccount` with themselves as `authority` first. Once initialized, the legitimate owner's own `InitializeNonceAccount` call fails (`State::Initialized(_) => Err(InstructionError::InvalidAccountData)`), and the attacker — now the recorded `authority` — can subsequently call `WithdrawNonceAccount`, which does check that the *authority* signed, to drain the account's lamports: [4](#0-3) 

The typical CLI/user flow avoids this by bundling `CreateAccount(WithSeed)` and `InitializeNonceAccount` atomically in a single transaction (see `create_nonce_account`/`create_nonce_account_with_seed` usage in `cli/src/nonce.rs`), but nothing in the protocol enforces this — any program or user that separates account creation from initialization into two transactions is exposed to the race, matching the report's "attacker frontruns the second transaction" scenario.

### Impact Explanation
A successful race lets an unprivileged attacker become the `authority` of another party's funded nonce account and then legitimately (per the withdraw-authorization check) withdraw all lamports from it via `WithdrawNonceAccount`. This is concrete value loss for the account's rightful funder/creator, achieved purely by an unprivileged third party observing a pending transaction and front-running it — the same failure mode (privileged action performed by the wrong party due to a missing ownership check during a two-step creation/initialization flow) as the referenced report.

### Likelihood Explanation
Exploitation requires that account creation (funding) and `InitializeNonceAccount` occur as two separate, observable transactions rather than atomically bundled — which is not enforced by the protocol and is plausible for custom tooling, programs, or offline-signing workflows that don't follow the CLI's bundled pattern. Given Solana's public mempool/leader schedule, front-running an unconfirmed second transaction is a well-understood and practical attack, making likelihood moderate for any workflow that separates the two steps.

### Recommendation
Require that `InitializeNonceAccount` be authorized by the same signer that funded/created the account (e.g., require the nonce account's own signature, or record and check a "pending creator" at `CreateAccount` time), so that only the party who funded the account can set its initial authority — analogous to the report's recommendation of not leaving ownership assignable by an arbitrary caller after creation.

### Proof of Concept
1. Victim submits `CreateAccountWithSeed` (or `CreateAccount`) funding a nonce-account pubkey `N`, intending to send a follow-up `InitializeNonceAccount(victim_authority)` transaction.
2. Attacker observes `N` is funded and system-owned with `State::Uninitialized`, and submits `InitializeNonceAccount(attacker_authority)` referencing `N` before the victim's second transaction lands — no signature from `N` or the victim is required per `initialize_nonce_account` (`programs/system/src/system_instruction.rs:163-201`) and `system_processor.rs:448-466`.
3. Victim's `InitializeNonceAccount` transaction now fails with `InstructionError::InvalidAccountData` since `N` is already `Initialized`.
4. Attacker calls `WithdrawNonceAccount` signed as `attacker_authority`, draining `N`'s lamports (`system_processor.rs:428-447`).

### Citations

**File:** programs/system/src/system_instruction.rs (L163-201)
```rust
pub(crate) fn initialize_nonce_account(
    account: &mut BorrowedInstructionAccount,
    nonce_authority: &Pubkey,
    rent: &Rent,
    invoke_context: &InvokeContext,
) -> Result<(), InstructionError> {
    if !account.is_writable() {
        ic_msg!(
            invoke_context,
            "Initialize nonce account: Account {} must be writeable",
            account.get_key()
        );
        return Err(InstructionError::InvalidArgument);
    }

    match account.get_state::<Versions>()?.state() {
        State::Uninitialized => {
            let min_balance = rent.minimum_balance(account.get_data().len());
            if account.get_lamports() < min_balance {
                ic_msg!(
                    invoke_context,
                    "Initialize nonce account: insufficient lamports {}, need {}",
                    account.get_lamports(),
                    min_balance
                );
                return Err(InstructionError::InsufficientFunds);
            }
            let durable_nonce =
                DurableNonce::from_blockhash(&invoke_context.environment_config.blockhash);
            let data = nonce::state::Data::new(
                *nonce_authority,
                durable_nonce,
                invoke_context
                    .environment_config
                    .blockhash_lamports_per_signature,
            );
            let state = State::Initialized(data);
            account.set_state(&Versions::new(state))
        }
```

**File:** programs/system/src/system_processor.rs (L117-135)
```rust
fn assign(
    account: &mut BorrowedInstructionAccount,
    address: &Address,
    owner: &Pubkey,
    signers: &HashSet<Pubkey>,
    invoke_context: &InvokeContext,
) -> Result<(), InstructionError> {
    // no work to do, just return
    if account.get_owner() == owner {
        return Ok(());
    }

    if !address.is_signer(signers) {
        ic_msg!(invoke_context, "Assign: account {:?} must sign", address);
        return Err(InstructionError::MissingRequiredSignature);
    }

    account.set_owner(&owner.to_bytes())
}
```

**File:** programs/system/src/system_processor.rs (L428-447)
```rust
        SystemInstruction::WithdrawNonceAccount(lamports) => {
            instruction_context.check_number_of_instruction_accounts(2)?;
            #[allow(deprecated)]
            let _recent_blockhashes = get_sysvar_with_account_check::recent_blockhashes(
                invoke_context,
                &instruction_context,
                2,
            )?;
            let rent =
                get_sysvar_with_account_check::rent(invoke_context, &instruction_context, 3)?;
            withdraw_nonce_account(
                0,
                lamports,
                1,
                &rent,
                &signers,
                invoke_context,
                &instruction_context,
            )
        }
```

**File:** programs/system/src/system_processor.rs (L448-466)
```rust
        SystemInstruction::InitializeNonceAccount(authorized) => {
            instruction_context.check_number_of_instruction_accounts(1)?;
            let mut me = instruction_context.try_borrow_instruction_account(0)?;
            #[allow(deprecated)]
            let recent_blockhashes = get_sysvar_with_account_check::recent_blockhashes(
                invoke_context,
                &instruction_context,
                1,
            )?;
            if recent_blockhashes.is_empty() {
                ic_msg!(
                    invoke_context,
                    "Initialize nonce account: recent blockhash list is empty",
                );
                return Err(SystemError::NonceNoRecentBlockhashes.into());
            }
            let rent =
                get_sysvar_with_account_check::rent(invoke_context, &instruction_context, 2)?;
            initialize_nonce_account(&mut me, &authorized, &rent, invoke_context)
```
