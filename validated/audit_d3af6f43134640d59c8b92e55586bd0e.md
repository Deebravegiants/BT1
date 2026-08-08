Based on my investigation, there is a real structural analog to the tSQD bug in the SVM nonce-account initialization path.

### Title
Missing signer/authority check on `InitializeNonceAccount` allows front-running takeover of a nonce account before its creator initializes it - (File: `programs/system/src/system_instruction.rs`)

### Summary
The Arbitrum report flags `registerTokenOnL2` as a permissionless, one-time-settable registration function that an attacker can front-run to permanently corrupt bridge state. The same bug class exists in agave's System Program nonce-account initialization: `initialize_nonce_account` sets a durable-nonce account's `authority` field the first time it transitions from `State::Uninitialized` to `State::Initialized`, but it enforces no signer/ownership check on who may call it — only that the account is writable and currently uninitialized.

### Finding Description
`initialize_nonce_account` only checks that the target account is writable and in `State::Uninitialized`, then unconditionally writes the supplied `nonce_authority` into the account and flips it to `State::Initialized`: [1](#0-0) 

Contrast this with the sibling `authorize_nonce_account` and `withdraw_nonce_account` functions, which both require a `signers: &HashSet<Pubkey>` set and validate the current authority against it before mutating the account: [2](#0-1) 

In the dispatcher, `SystemInstruction::InitializeNonceAccount(authorized)` is routed straight to `initialize_nonce_account` without any signer/authority validation on the nonce account itself, unlike `WithdrawNonceAccount` and `AuthorizeNonceAccount`, which pass `&signers` derived from the transaction's actual signatures: [3](#0-2) 

Because the account is only required to be writable (not a signer) at this instruction, once a system-owned, rent-exempt, appropriately-sized account exists on-chain in the `Uninitialized` nonce state (e.g., created by a separate prior `CreateAccount` call, rather than atomically bundled with `InitializeNonceAccount` in the same transaction), *any* unprivileged party can submit their own transaction naming that account (non-signer, writable) and call `InitializeNonceAccount` with an attacker-chosen `authority`. Once `State::Initialized` is set, re-initialization is explicitly rejected (`InstructionError::InvalidAccountData` for the `State::Initialized` branch), so the hijack is permanent and unrecoverable by the legitimate creator — mirroring the tSQD `shouldRegisterGateway` one-shot flag that can never be corrected once triggered.

### Impact Explanation
An attacker who wins this race becomes the sole nonce authority: they gain exclusive rights to advance the durable nonce (invalidating any transaction pre-signed against it) and to withdraw all lamports from the account via `withdraw_nonce_account`, which enforces the (now attacker-controlled) authority. The legitimate owner loses all use of the account and any funds already deposited into it, with no path to reclaim authority — a concrete value-loss/undeclared-account-mutation outcome, analogous to the "bridge token broken and unable to be changed" impact in the report.

### Likelihood Explanation
Exploitation requires the victim to create the system account and initialize it as a nonce account in two separate transactions (rather than atomically), giving an attacker monitoring the mempool/first transaction a window to front-run the second. Standard SDK helpers typically bundle `CreateAccount` + `InitializeNonceAccount` into a single transaction precisely to avoid this window, which lowers likelihood for default tooling but does not change the fact that the on-chain instruction itself performs no signer/authority check — any caller who can observe an uninitialized, rent-exempt, correctly-sized system-owned account can race to claim it.

### Recommendation
Require `InitializeNonceAccount` to validate that the account (or a designated creator/authority) is an actual transaction signer before transitioning from `Uninitialized` to `Initialized`, mirroring the signer-set checks already used in `authorize_nonce_account` and `withdraw_nonce_account`.

### Proof of Concept
1. Party A submits `SystemInstruction::CreateAccount` funding a new keypair `N` with `nonce::state::State::size()` bytes and rent-exempt lamports, owned by the System Program (a separate transaction from initialization).
2. Once that transaction lands, an attacker observes account `N` on-chain in `State::Uninitialized`.
3. The attacker submits a new transaction (any fee payer) with `SystemInstruction::InitializeNonceAccount(attacker_pubkey)`, listing `N` as `AccountMeta { is_signer: false, is_writable: true }` — no signature over `N` is required by `initialize_nonce_account`.
4. The dispatcher in `system_processor.rs` routes this straight to `initialize_nonce_account`, which sets `N`'s authority to `attacker_pubkey` and flips state to `Initialized`.
5. Party A's subsequent legitimate `InitializeNonceAccount(A_authority)` now hits the `State::Initialized(_)` branch and fails with `InstructionError::InvalidAccountData`, permanently locking A out while the attacker controls the account via `AuthorizeNonceAccount`/`WithdrawNonceAccount`.

### Citations

**File:** programs/system/src/system_instruction.rs (L163-211)
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
        State::Initialized(_) => {
            ic_msg!(
                invoke_context,
                "Initialize nonce account: Account {} state is invalid",
                account.get_key()
            );
            Err(InstructionError::InvalidAccountData)
        }
    }
}
```

**File:** programs/system/src/system_instruction.rs (L213-249)
```rust
pub(crate) fn authorize_nonce_account(
    account: &mut BorrowedInstructionAccount,
    nonce_authority: &Pubkey,
    signers: &HashSet<Pubkey>,
    invoke_context: &InvokeContext,
) -> Result<(), InstructionError> {
    if !account.is_writable() {
        ic_msg!(
            invoke_context,
            "Authorize nonce account: Account {} must be writeable",
            account.get_key()
        );
        return Err(InstructionError::InvalidArgument);
    }
    match account
        .get_state::<Versions>()?
        .authorize(signers, *nonce_authority)
    {
        Ok(versions) => account.set_state(&versions),
        Err(AuthorizeNonceError::Uninitialized) => {
            ic_msg!(
                invoke_context,
                "Authorize nonce account: Account {} state is invalid",
                account.get_key()
            );
            Err(InstructionError::InvalidAccountData)
        }
        Err(AuthorizeNonceError::MissingRequiredSignature(account_authority)) => {
            ic_msg!(
                invoke_context,
                "Authorize nonce account: Account {} must sign",
                account_authority
            );
            Err(InstructionError::MissingRequiredSignature)
        }
    }
}
```

**File:** programs/system/src/system_processor.rs (L428-467)
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
        }
```
