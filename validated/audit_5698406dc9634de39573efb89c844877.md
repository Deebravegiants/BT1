### Title
`InitializeNonceAccount` performs no signer/authority check, allowing an attacker to front-run initialization of a pre-funded nonce account and steal its lamports - ([File: programs/system/src/system_instruction.rs])

### Summary
The `SystemInstruction::InitializeNonceAccount` handler sets the nonce account's authority to an attacker-supplied `authorized` pubkey without requiring any signature from the account itself or its intended creator. If account funding/allocation (via `CreateAccount`/`Allocate`+`Assign`) and the subsequent `InitializeNonceAccount` call are not atomically bundled in the exact same transaction (a pattern that is entirely possible for any third-party integrator or a multi-step client flow that doesn't follow the SDK's `create_nonce_account` helper), an attacker observing the mempool can front-run the initialization step, set themselves as `nonce_authority`, and later drain the account's lamports via `WithdrawNonceAccount`. This mirrors the reported DAOfi bug: a resource is deposited into/created at a deterministic, permissionless slot, but a *separate*, unauthenticated initialization step decides who controls it, letting an attacker "adopt" the victim's funded resource before the victim's own initialization lands.

### Finding Description
`initialize_nonce_account()` only checks that the target account is writable and that its state is `Uninitialized`; it does not verify that the caller, the account, or any related keypair signed the transaction: [1](#0-0) 

Compare this to `advance_nonce_account()` and `withdraw_nonce_account()`, which both explicitly require `signers.contains(&data.authority)`/`check_signer(&data.authority)` before acting on an already-initialized nonce account: [2](#0-1) [3](#0-2) 

The dispatcher in `system_processor.rs` confirms `InitializeNonceAccount` requires only one account (the nonce account itself), with no signer set passed into `initialize_nonce_account`: [4](#0-3) 

By contrast, `CreateAccount` explicitly requires the `to` address to be a signer via `Address::is_signer`, which is the control that normally prevents someone else from "claiming" a brand-new address: [5](#0-4) [6](#0-5) 

This creates a gap analogous to the DAOfi report: a victim can allocate/fund a system-owned account sized for nonce state (e.g., via `Allocate`+`Assign`, or by simply funding an address that was already allocated earlier) in one step, and only later submit `InitializeNonceAccount` to set the intended `nonce_authority`. Because `InitializeNonceAccount` requires no signature at all, any unprivileged attacker who sees the funded-but-uninitialized account can submit their own `InitializeNonceAccount(attacker_pubkey)` first. The transaction ordering within a block/slot is determined by fee-payer priority and leader scheduling, not by who "owns" the account, so a higher-fee or well-timed attacker transaction can land first.

Once `Initialized(Data { authority: attacker_pubkey, .. })` is committed, the attacker is the sole `authority` recognized by `advance_nonce_account` and `withdraw_nonce_account`, and can immediately withdraw all lamports the victim funded into the account via `WithdrawNonceAccount`: [7](#0-6) 

### Impact Explanation
This results in concrete, permanent loss of funds for any unprivileged user who funds a nonce-account-shaped account (rent-exempt lamports plus correct data length) and does not initialize it in the exact same atomic transaction as its funding/allocation. The Solana CLI and SDK helpers avoid this by bundling `CreateAccount` + `InitializeNonceAccount` into a single transaction, so the default CLI path is not directly exposed. However, any custom tooling, program, or multi-step flow that separates funding from initialization is exploitable by an unprivileged network observer, resulting in direct value theft with no privileged role required by the attacker.

### Likelihood Explanation
Exploitation requires: (1) an account that is system-owned, sized for `nonce::state::Versions`, rent-exempt, and in `State::Uninitialized`, existing in a state visible before the legitimate initialization lands, and (2) the attacker being able to land their `InitializeNonceAccount` transaction before the victim's. Since transaction ordering can be influenced by fee/priority and mempool visibility, this is realistically exploitable whenever funding and initialization are split across transactions — a pattern outside the default CLI flow but plausible for third-party integrators/wallets building nonce accounts manually or programmatically (e.g., pre-funding a PDA/derived nonce address before invoking initialization from a separate instruction/transaction).

### Recommendation
Require `InitializeNonceAccount` to check that the account itself (or a caller-nominated signer matching the account key) is a transaction signer, consistent with the signer requirement already enforced by `CreateAccount`. Alternatively/additionally, document and encourage that nonce account funding and initialization always occur atomically in the same transaction, and consider adding a runtime check rejecting `InitializeNonceAccount` on accounts that were not created in the same transaction (mirroring the "created-and-initialized together" invariant recommended in the original report for pair creation and deposit).

### Proof of Concept
1. Victim submits a transaction that only allocates and funds a system-owned account `N` to the exact size/rent-exemption required for `nonce::state::Versions` (e.g., via `Allocate` + `Assign` to the system program, or `CreateAccount` where `N` is itself the fee payer/signer but the same transaction does not include `InitializeNonceAccount`).
2. Attacker observes account `N` in `State::Uninitialized` with rent-exempt lamports, before the victim's follow-up `InitializeNonceAccount` transaction lands.
3. Attacker submits `SystemInstruction::InitializeNonceAccount(attacker_pubkey)` targeting `N` with higher priority fee; per `initialize_nonce_account()` no signature over `N` or its intended owner is required, only that `N` is writable and `Uninitialized`: [8](#0-7) 
4. This transaction lands first, setting `authority = attacker_pubkey`.
5. Victim's own `InitializeNonceAccount` now fails (`State::Initialized(_) => Err(InstructionError::InvalidAccountData)`), confirming the hijack: [9](#0-8) 
6. Attacker calls `WithdrawNonceAccount` with themselves as the signing `authority`, draining all lamports the victim deposited into `N`: [10](#0-9) 

**Note on confidence:** This is a structural analog verified directly in `programs/system/src/system_instruction.rs` and `system_processor.rs`. I was not able to fully verify, given index limits, whether any additional runtime-level guard exists elsewhere (e.g., in `runtime`/`accounts-db` transaction-account-loading code) that might implicitly force atomic funding+initialization for all callers beyond the SDK's own convention; a full audit of all instruction-building call sites across the workspace would require a Devin session with complete repository access to be exhaustive.

### Citations

**File:** programs/system/src/system_instruction.rs (L39-49)
```rust
    let state: Versions = account.get_state()?;
    match state.state() {
        State::Initialized(data) => {
            if !signers.contains(&data.authority) {
                ic_msg!(
                    invoke_context,
                    "Advance nonce account: Account {} must be a signer",
                    data.authority
                );
                return Err(InstructionError::MissingRequiredSignature);
            }
```

**File:** programs/system/src/system_instruction.rs (L80-161)
```rust
pub(crate) fn withdraw_nonce_account(
    from_account_index: IndexOfAccount,
    lamports: u64,
    to_account_index: IndexOfAccount,
    rent: &Rent,
    signers: &HashSet<Pubkey>,
    invoke_context: &InvokeContext,
    instruction_context: &InstructionContext,
) -> Result<(), InstructionError> {
    let mut from = instruction_context.try_borrow_instruction_account(from_account_index)?;
    if !from.is_writable() {
        ic_msg!(
            invoke_context,
            "Withdraw nonce account: Account {} must be writeable",
            from.get_key()
        );
        return Err(InstructionError::InvalidArgument);
    }

    let check_signer = |signer: &Pubkey| {
        if !signers.contains(signer) {
            ic_msg!(
                invoke_context,
                "Withdraw nonce account: Account {} must sign",
                signer
            );
            return Err(InstructionError::MissingRequiredSignature);
        }
        Ok(())
    };

    let state: Versions = from.get_state()?;
    match state.state() {
        State::Uninitialized => {
            if lamports > from.get_lamports() {
                ic_msg!(
                    invoke_context,
                    "Withdraw nonce account: insufficient lamports {}, need {}",
                    from.get_lamports(),
                    lamports,
                );
                return Err(InstructionError::InsufficientFunds);
            }
            check_signer(from.get_key())?;
        }
        State::Initialized(data) => {
            if lamports == from.get_lamports() {
                let durable_nonce =
                    DurableNonce::from_blockhash(&invoke_context.environment_config.blockhash);
                if data.durable_nonce == durable_nonce {
                    ic_msg!(
                        invoke_context,
                        "Withdraw nonce account: nonce can only advance once per slot"
                    );
                    return Err(SystemError::NonceBlockhashNotExpired.into());
                }
                check_signer(&data.authority)?;
                from.set_state(&Versions::new(State::Uninitialized))?;
            } else {
                let min_balance = rent.minimum_balance(from.get_data().len());
                let amount = checked_add(lamports, min_balance)?;
                if amount > from.get_lamports() {
                    ic_msg!(
                        invoke_context,
                        "Withdraw nonce account: insufficient lamports {}, need {}",
                        from.get_lamports(),
                        amount,
                    );
                    return Err(InstructionError::InsufficientFunds);
                }
                check_signer(&data.authority)?;
            }
        }
    };

    from.checked_sub_lamports(lamports)?;
    drop(from);
    let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
    to.checked_add_lamports(lamports)?;

    Ok(())
}
```

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

**File:** programs/system/src/system_instruction.rs (L202-209)
```rust
        State::Initialized(_) => {
            ic_msg!(
                invoke_context,
                "Initialize nonce account: Account {} state is invalid",
                account.get_key()
            );
            Err(InstructionError::InvalidAccountData)
        }
```

**File:** programs/system/src/system_processor.rs (L27-72)
```rust
// represents an address that may or may not have been generated
//  from a seed
#[derive(PartialEq, Eq, Default, Debug)]
struct Address {
    address: Pubkey,
    base: Option<Pubkey>,
}

impl Address {
    fn is_signer(&self, signers: &HashSet<Pubkey>) -> bool {
        if let Some(base) = self.base {
            signers.contains(&base)
        } else {
            signers.contains(&self.address)
        }
    }
    fn create(
        address: &Pubkey,
        with_seed: Option<(&Pubkey, &str, &Pubkey)>,
        invoke_context: &InvokeContext,
    ) -> Result<Self, InstructionError> {
        let base = if let Some((base, seed, owner)) = with_seed {
            // The conversion from `PubkeyError` to `InstructionError` through
            // num-traits is incorrect, but it's the existing behavior.
            let address_with_seed =
                Pubkey::create_with_seed(base, seed, owner).map_err(|e| e as u64)?;
            // re-derive the address, must match the supplied address
            if *address != address_with_seed {
                ic_msg!(
                    invoke_context,
                    "Create: address {} does not match derived address {}",
                    address,
                    address_with_seed
                );
                return Err(SystemError::AddressWithSeedMismatch.into());
            }
            Some(*base)
        } else {
            None
        };

        Ok(Self {
            address: *address,
            base,
        })
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
