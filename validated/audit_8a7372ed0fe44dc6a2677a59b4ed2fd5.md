Confirmed: neither `initialize_nonce_account` nor `authorize_nonce_account` in `programs/system/src/system_instruction.rs` validate that the supplied `nonce_authority`/`new_authority` pubkey is non-default. Test `authorize_inx_ok` even exercises setting the authority to `Pubkey::default()` and it succeeds. This is a legitimate self-inflicted-but-reachable analog to the reported "missing zero-address validation in constructor" bug class: it permanently locks value in an unprivileged-user-owned account, reachable purely through the System Program's nonce instructions (no operator role needed).

### Title
Missing Validation of Nonce Authority Allows Permanent Lockup of Durable Nonce Account Funds - (File: programs/system/src/system_instruction.rs)

### Summary
`initialize_nonce_account` and `authorize_nonce_account` accept an arbitrary `nonce_authority`/`new_authority` `Pubkey` and store it into the nonce account's `Data::authority` field without checking that it is non-default (i.e., not `Pubkey::default()`, the all-zero pubkey) or otherwise attacker/user-unreachable. [1](#0-0) [2](#0-1) 

### Finding Description
`initialize_nonce_account` writes `*nonce_authority` directly into `nonce::state::Data::new(...)` with no non-zero/well-formed check on the value. [3](#0-2) 
Likewise, `authorize_nonce_account` re-assigns the authority via `Versions::authorize(signers, *nonce_authority)` with no validation of the new value beyond requiring the *current* authority to sign. [2](#0-1) 

All subsequent privileged operations on the nonce account — advancing the nonce and withdrawing lamports while `Initialized` — require a signer matching `data.authority`:
- `advance_nonce_account` checks `signers.contains(&data.authority)`. [4](#0-3) 
- `withdraw_nonce_account`'s `State::Initialized` branch calls `check_signer(&data.authority)` for both the full-balance and partial-withdrawal paths. [5](#0-4) 

If `authority` is ever set to `Pubkey::default()` (or any other pubkey nobody controls the private key for), no transaction can ever produce a matching signer for that key, since `check_signer`/`signers.contains` require a real Ed25519 signature over the transaction. Both the advance and withdraw code paths become permanently unreachable for that nonce account, and the tests demonstrate the state transition succeeds with `Pubkey::default()` as the authority with no error. [6](#0-5) 

This mirrors the reported bug class: a constructor/initializer parameter (`owner`/`compliance` in the external report, `nonce_authority` here) is stored unchecked, and a zero/unusable value permanently bricks the object (the ERC-20 token vs. the on-chain nonce account), locking any value held by it.

### Impact Explanation
Once a durable nonce account's authority is set (via `InitializeNonceAccount` or `AuthorizeNonceAccount`) to `Pubkey::default()` or any other pubkey without a discoverable private key, the lamports held in the nonce account (at minimum the rent-exempt minimum balance, but potentially more if the owner deposited extra funds before/without immediately advancing) become permanently unretrievable — no future transaction can supply the required signer for `data.authority`, so `withdraw_nonce_account`'s `Initialized` branch can never succeed. This is a concrete, permanent loss of value on an unprivileged, ordinary user code path.

### Likelihood Explanation
This requires no attacker/validator privilege and is reachable by any user submitting an ordinary `InitializeNonceAccount` or `AuthorizeNonceAccount` instruction (e.g., via a buggy client, malformed derivation, or accidental default-value substitution) — the same class of accidental misconfiguration that the external USDKG report calls out. Given wallets/tools compute `nonce_authority` from user input, an unvalidated zero/garbage pubkey can slip through unnoticed until funds are already locked.

### Recommendation
Add a check in `initialize_nonce_account` and `authorize_nonce_account` (in `programs/system/src/system_instruction.rs`) rejecting `nonce_authority == Pubkey::default()` (and consider rejecting other known-unusable values), returning `InstructionError::InvalidArgument` similar to the existing writability checks. [7](#0-6) 

### Proof of Concept
1. Create and fund a nonce account, then call `InitializeNonceAccount(Pubkey::default())` (or `AuthorizeNonceAccount(Pubkey::default())` on an already-initialized account) — this succeeds as shown by `authorize_inx_ok` in the test module. [6](#0-5) 
2. Attempt `AdvanceNonceAccount` or `WithdrawNonceAccount` on this account — every subsequent attempt fails `MissingRequiredSignature` since no signer can match `Pubkey::default()`. [4](#0-3) [5](#0-4) 
3. The account's lamports are permanently locked with no recovery path.

### Citations

**File:** programs/system/src/system_instruction.rs (L41-49)
```rust
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

**File:** programs/system/src/system_instruction.rs (L125-151)
```rust
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
```

**File:** programs/system/src/system_instruction.rs (L163-200)
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
```

**File:** programs/system/src/system_instruction.rs (L213-231)
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
```

**File:** programs/system/src/system_instruction.rs (L1010-1037)
```rust
    #[test]
    fn authorize_inx_ok() {
        prepare_mockup!(
            invoke_context,
            instruction_accounts,
            rent,
            transaction_context
        );
        push_instruction_context!(invoke_context, instruction_context, instruction_accounts);
        let mut nonce_account = instruction_context
            .try_borrow_instruction_account(NONCE_ACCOUNT_INDEX)
            .unwrap();
        let mut signers = HashSet::new();
        signers.insert(*nonce_account.get_key());
        set_invoke_context_blockhash!(invoke_context, 31);
        let authorized = *nonce_account.get_key();
        initialize_nonce_account(&mut nonce_account, &authorized, &rent, &invoke_context).unwrap();
        let authority = Pubkey::default();
        let data = nonce::state::Data::new(
            authority,
            DurableNonce::from_blockhash(&invoke_context.environment_config.blockhash),
            invoke_context
                .environment_config
                .blockhash_lamports_per_signature,
        );
        authorize_nonce_account(&mut nonce_account, &authority, &signers, &invoke_context).unwrap();
        let versions = nonce_account.get_state::<Versions>().unwrap();
        assert_eq!(versions.state(), &State::Initialized(data));
```
