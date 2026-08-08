### Title
Unauthenticated `InitializeBuffer` Allows Front-Running Theft of BPF Upgradeable Buffer Authority - (File: programs/bpf_loader/src/lib.rs)

### Summary
`UpgradeableLoaderInstruction::InitializeBuffer` in the BPF Upgradeable Loader sets a buffer account's `authority_address` to whatever pubkey is passed as instruction account index 1, with no signature check on that account and no requirement that the caller who created the buffer account is the one initializing it. [1](#0-0)  This mirrors the reported `NoteERC20.initialize()` front-running class: create-then-initialize is a two-step, non-atomic pattern, and the initialize step has no ownership check.

### Finding Description
The System Program's `CreateAccount` only allocates space/lamports and assigns ownership to the BPF Upgradeable Loader — it does not set any loader-level state. [2](#0-1)  The buffer only becomes a usable "Buffer" with a real authority once `InitializeBuffer` runs. Looking at `process_loader_upgradeable_instruction`:

```
UpgradeableLoaderInstruction::InitializeBuffer => {
    instruction_context.check_number_of_instruction_accounts(2)?;
    let mut buffer = instruction_context.try_borrow_instruction_account(0)?;
    if UpgradeableLoaderState::Uninitialized != buffer.get_state()? {
        return Err(InstructionError::AccountAlreadyInitialized);
    }
    let authority_key = Some(*instruction_context.get_key_of_instruction_account(1)?);
    buffer.set_state(&UpgradeableLoaderState::Buffer { authority_address: authority_key })?;
}
``` [1](#0-0) 

Notice that unlike every other branch of the same match statement (`Write`, `DeployWithMaxDataLen`, `Upgrade`, `SetAuthority`, `SetAuthorityChecked`), `InitializeBuffer` never calls `instruction_context.is_instruction_account_signer(...)` and never checks that account 0 (the buffer) itself is a signer. [3](#0-2)  Anyone can submit an `InitializeBuffer` instruction referencing any account currently in `UpgradeableLoaderState::Uninitialized`, and set the `authority_address` to any pubkey they choose (including their own).

The intended safe usage bundles `CreateAccount` + `InitializeBuffer` atomically via `solana_loader_v3_interface::instruction::create_buffer`, as seen in tests and `runtime/src/loader_utils.rs::load_upgradeable_buffer`, which builds both instructions into a single `Message`/transaction. [4](#0-3)  However, nothing in the on-chain program enforces that atomicity — it is only a client-side convention followed by the CLI (`cli/src/program.rs` `WriteBuffer`) and `create_buffer` helper. If a user (or any deployment tooling not using the bundled helper) submits `CreateAccount` for the buffer and `InitializeBuffer` as two separate transactions, the intervening window is directly exploitable: an attacker observing the mempool/confirmed `CreateAccount` for the freshly-created, still-`Uninitialized` buffer account can race their own `InitializeBuffer` transaction naming themselves as `authority_address` before the legitimate deployer's `InitializeBuffer` lands.

### Impact Explanation
Once an attacker's `InitializeBuffer` transaction lands first, the legitimate user's own `InitializeBuffer` for the same buffer account will fail with `AccountAlreadyInitialized` (see the "already initialized" branch), permanently denying the intended deployer control of that buffer. [5](#0-4)  The buffer account is now owned (in terms of authority) by the attacker: only the attacker can `Write` program bytes into it or feed it into `DeployWithMaxDataLen`, both of which check `authority_address` against the signer. [6](#0-5) [7](#0-6)  The victim's rent/lamports funding the account creation are effectively stranded (the account cannot be reclaimed by the legitimate party since `Close`/`SetAuthority` both require the current — now attacker-controlled — authority to sign). This is a concrete denial-of-service and loss-of-control over pre-funded state, directly analogous to the reported `NoteERC20.initialize()` front-running DoS: unrecoverable rent/gas expenses and inability to complete the intended program deployment.

### Likelihood Explanation
Exploitation requires only that a deployer split `CreateAccount` and `InitializeBuffer` into separate transactions (or that the two land in different slots/be revert-able for other reasons), which can happen with any custom deployment tooling or SDK usage that does not follow the `create_buffer` bundling convention (analogous to `scripts/deployment.py` in the original report not bundling proxy deploy+init). Any unprivileged network participant can observe pending/confirmed buffer `CreateAccount` transactions and race an `InitializeBuffer` instruction naming themselves as authority — no special privileges, validator role, or protocol feature gating is needed, and the instruction handler itself performs zero authentication.

### Recommendation
Require that `InitializeBuffer` verifies a signer for either the buffer account itself or the proposed `authority_address`, matching the pattern already used by `Write`, `Upgrade`, `SetAuthority`, and `SetAuthorityChecked` (which all check `instruction_context.is_instruction_account_signer(...)`). [8](#0-7)  At minimum, require the account creator (via a `CreateAccount`-time owner assertion) or the designated authority to sign the `InitializeBuffer` instruction before writing `authority_address`.

### Proof of Concept
1. Victim submits `system_instruction::create_account(payer, buffer_pubkey, lamports, size, bpf_loader_upgradeable::id())` as its own transaction (not bundled with `InitializeBuffer`), per the two-step pattern shown to be structurally decomposable in `solana_loader_v3_interface::instruction::create_buffer` (which normally emits both instructions together, but nothing prevents sending them separately).
2. Once this transaction confirms, `buffer_pubkey`'s account is owned by `bpf_loader_upgradeable::id()` with state `UpgradeableLoaderState::Uninitialized`.
3. Attacker submits `UpgradeableLoaderInstruction::InitializeBuffer` with accounts `[buffer_pubkey (writable), attacker_pubkey]`. Per `process_loader_upgradeable_instruction`, no signer check is performed on either account, so this succeeds, setting `authority_address = Some(attacker_pubkey)`. [1](#0-0) 
4. Victim's follow-up `InitializeBuffer` transaction (naming victim as authority) now fails with `InstructionError::AccountAlreadyInitialized`. [5](#0-4) 
5. Only the attacker can subsequently `Write` to or deploy from `buffer_pubkey`; the victim's rent-exempt lamports are stuck under attacker-controlled authority.

### Citations

**File:** programs/bpf_loader/src/lib.rs (L158-172)
```rust
        UpgradeableLoaderInstruction::InitializeBuffer => {
            instruction_context.check_number_of_instruction_accounts(2)?;
            let mut buffer = instruction_context.try_borrow_instruction_account(0)?;

            if UpgradeableLoaderState::Uninitialized != buffer.get_state()? {
                ic_logger_msg!(log_collector, "Buffer account already initialized");
                return Err(InstructionError::AccountAlreadyInitialized);
            }

            let authority_key = Some(*instruction_context.get_key_of_instruction_account(1)?);

            buffer.set_state(&UpgradeableLoaderState::Buffer {
                authority_address: authority_key,
            })?;
        }
```

**File:** programs/bpf_loader/src/lib.rs (L177-190)
```rust
            if let UpgradeableLoaderState::Buffer { authority_address } = buffer.get_state()? {
                if authority_address.is_none() {
                    ic_logger_msg!(log_collector, "Buffer is immutable");
                    return Err(InstructionError::Immutable); // TODO better error code
                }
                let authority_key = Some(*instruction_context.get_key_of_instruction_account(1)?);
                if authority_address != authority_key {
                    ic_logger_msg!(log_collector, "Incorrect buffer authority provided");
                    return Err(InstructionError::IncorrectAuthority);
                }
                if !instruction_context.is_instruction_account_signer(1)? {
                    ic_logger_msg!(log_collector, "Buffer authority did not sign");
                    return Err(InstructionError::MissingRequiredSignature);
                }
```

**File:** programs/bpf_loader/src/lib.rs (L242-250)
```rust
            if let UpgradeableLoaderState::Buffer { authority_address } = buffer.get_state()? {
                if authority_address != authority_key {
                    ic_logger_msg!(log_collector, "Buffer and upgrade authority don't match");
                    return Err(InstructionError::IncorrectAuthority);
                }
                if !instruction_context.is_instruction_account_signer(7)? {
                    ic_logger_msg!(log_collector, "Upgrade authority did not sign");
                    return Err(InstructionError::MissingRequiredSignature);
                }
```

**File:** programs/bpf_loader/src/lib.rs (L549-592)
```rust
        UpgradeableLoaderInstruction::SetAuthority => {
            instruction_context.check_number_of_instruction_accounts(2)?;
            let mut account = instruction_context.try_borrow_instruction_account(0)?;
            let present_authority_key = instruction_context.get_key_of_instruction_account(1)?;
            let new_authority = instruction_context.get_key_of_instruction_account(2).ok();

            match account.get_state()? {
                UpgradeableLoaderState::Buffer { authority_address } => {
                    if new_authority.is_none() {
                        ic_logger_msg!(log_collector, "Buffer authority is not optional");
                        return Err(InstructionError::IncorrectAuthority);
                    }
                    if authority_address.is_none() {
                        ic_logger_msg!(log_collector, "Buffer is immutable");
                        return Err(InstructionError::Immutable);
                    }
                    if authority_address != Some(*present_authority_key) {
                        ic_logger_msg!(log_collector, "Incorrect buffer authority provided");
                        return Err(InstructionError::IncorrectAuthority);
                    }
                    if !instruction_context.is_instruction_account_signer(1)? {
                        ic_logger_msg!(log_collector, "Buffer authority did not sign");
                        return Err(InstructionError::MissingRequiredSignature);
                    }
                    account.set_state(&UpgradeableLoaderState::Buffer {
                        authority_address: new_authority.cloned(),
                    })?;
                }
                UpgradeableLoaderState::ProgramData {
                    slot,
                    upgrade_authority_address,
                } => {
                    if upgrade_authority_address.is_none() {
                        ic_logger_msg!(log_collector, "Program not upgradeable");
                        return Err(InstructionError::Immutable);
                    }
                    if upgrade_authority_address != Some(*present_authority_key) {
                        ic_logger_msg!(log_collector, "Incorrect upgrade authority provided");
                        return Err(InstructionError::IncorrectAuthority);
                    }
                    if !instruction_context.is_instruction_account_signer(1)? {
                        ic_logger_msg!(log_collector, "Upgrade authority did not sign");
                        return Err(InstructionError::MissingRequiredSignature);
                    }
```

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

**File:** runtime/src/loader_utils.rs (L88-107)
```rust
    bank_client
        .send_and_confirm_message(
            &[from_keypair, buffer_keypair],
            Message::new(
                &solana_loader_v3_interface::instruction::create_buffer(
                    &from_keypair.pubkey(),
                    &buffer_pubkey,
                    &buffer_authority_pubkey,
                    1.max(
                        bank_client
                            .get_minimum_balance_for_rent_exemption(program_buffer_bytes)
                            .unwrap(),
                    ),
                    program.len(),
                )
                .unwrap(),
                Some(&from_keypair.pubkey()),
            ),
        )
        .unwrap();
```
