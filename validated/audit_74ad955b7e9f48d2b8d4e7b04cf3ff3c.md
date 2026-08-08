### Title
Program deployment griefing via pre-funded ProgramData PDA blocks `DeployWithMaxDataLen` permanently - (File: `programs/bpf_loader/src/lib.rs`)

### Summary
`UpgradeableLoaderInstruction::DeployWithMaxDataLen` derives the new program's `ProgramData` address deterministically via `find_program_address(&[new_program_id.as_ref()], program_id)` and then creates that account by invoking the plain `system_instruction::create_account`, which fails outright if the target address already holds any lamports. Any unprivileged user can pre-fund that deterministic PDA with a trivial system `Transfer` before the legitimate deployer submits the deployment transaction, permanently blocking deployment of the program to that address — the same class of "deterministic-address preemption" attack described in the Nibiru vesting-account report, where an attacker races to occupy a predictable future address so it can never be legitimately initialized.

### Finding Description
In `process_loader_upgradeable_instruction`, the `DeployWithMaxDataLen` handler derives the ProgramData PDA and creates it via a native CPI to the System Program's `CreateAccount` instruction: [1](#0-0) 

The System Program's `create_account` function unconditionally rejects account creation if the destination already has a positive lamport balance: [2](#0-1) 

Because the ProgramData address is a Program Derived Address (no corresponding private key exists), any lamports sent to it via an ordinary `Transfer` (which requires no signature from the *recipient*) can never be reclaimed or reassigned by anyone except through this same `create_account` flow, which will always fail once `lamports > 0`. Since `new_program_id` (the future program key) is commonly a keypair chosen/publicized ahead of time (vanity addresses, reproducible CI-generated deploy keys, previously-announced program IDs), an attacker who learns or predicts that address can front-run the deployer with a 1-lamport transfer to the derived ProgramData PDA, after which the deploy transaction will always abort with `SystemError::AccountAlreadyInUse` inside `create_account` (line 170), rolling back the whole instruction.

This mirrors the analog reported in Nibiru: an attacker preemptively occupies a deterministic future address so the legitimate account/contract can never be properly initialized there, permanently orphaning the intended deployment target.

Note: the codebase already contains a fix pattern for exactly this class of bug — a newer `SystemInstruction::CreateAccountAllowPrefund` variant explicitly designed to tolerate a pre-funded destination: [3](#0-2) 
However `programs/bpf_loader/src/lib.rs` still uses the legacy, prefund-intolerant `system_instruction::create_account` for `DeployWithMaxDataLen`, so this specific SVM-loading path was not migrated to the new, safer instruction (confirmed via search — `create_account_allow_prefund` is referenced only in `feature-set`, `system_processor.rs`, benches, `cost-model`, `svm-feature-set`, and `transaction-status`, never in `programs/bpf_loader`).

### Impact Explanation
Any unprivileged actor can permanently deny program deployment to a specific, predictable program address for the cost of a single dust `Transfer` transaction. This is a concrete denial-of-service against normal SVM program-loading (loader v3/`bpf_loader_upgradeable`, which is explicitly in scope, unlike Loader V4). Impact is amplified for high-value/publicized program addresses (vanity/branded program IDs announced before deployment), where the target deployer's rent-paid Program/Buffer accounts remain unusable for that address and the deployer must switch to a completely different program ID, undermining any pre-announced address commitments. This qualifies as concrete value loss/griefing consistent with the accepted "materially underpriced execution"/DoS bug class, achievable purely with unprivileged, ordinary transactions (no validator or operator role required).

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to know the future `new_program_id` before the deploy transaction lands (e.g., vanity keypairs generated offline and shared, deterministic CI/CD deployer keys, or a program address announced publicly in advance for marketing/composability reasons). This is a realistic and previously acknowledged real-world pattern in Solana tooling (deployers frequently pre-generate and publish/commit to a program keypair before actually deploying). The attack itself is trivial and cheap — a single `Transfer` instruction of 1 lamport to the derived PDA — reachable by any user with a funded account.

### Recommendation
Migrate `DeployWithMaxDataLen` (and any other loader-v3 code path that creates a PDA-derived account, e.g. `programs/bpf_loader/src/lib.rs` around line 296) to use the already-implemented `SystemInstruction::CreateAccountAllowPrefund` (gated by the `create_account_allow_prefund` feature) instead of the legacy `system_instruction::create_account`, so that pre-funding the ProgramData address with stray lamports no longer blocks legitimate creation. Alternatively/additionally, have the loader explicitly detect a non-zero-lamport, empty, system-owned ProgramData account and treat it as fundable (sweep/absorb the existing lamports) rather than failing outright.

### Proof of Concept
1. Deployer generates (or publicly commits to) a future program keypair `P` (e.g., a vanity address) and intends to deploy via `bpf_loader_upgradeable::deploy_with_max_program_len`.
2. Attacker computes `programdata_key = find_program_address(&[P.as_ref()], bpf_loader_upgradeable::id())` off-chain and sends a `system_instruction::transfer` of 1 lamport from any funded account to `programdata_key`.
3. Deployer submits the normal `DeployWithMaxDataLen`/`deploy_with_max_program_len` transaction for program `P`.
4. Inside `process_loader_upgradeable_instruction`, the native CPI to `system_instruction::create_account(&payer_key, &programdata_key, ...)` hits the check `to.get_lamports() > 0` in `create_account` (`programs/system/src/system_processor.rs:164-171`) and returns `SystemError::AccountAlreadyInUse`, aborting the whole instruction/transaction.
5. Because `programdata_key` is a PDA with no private key, no one can ever transfer its lamports away or otherwise clear it outside of the `bpf_loader_upgradeable` program itself invoking `create_account`/`allocate` with matching seeds — which will always hit the same `lamports > 0` check first. Deployment to program ID `P` is permanently blocked.

### Citations

**File:** programs/bpf_loader/src/lib.rs (L279-310)
```rust
            // Create ProgramData account
            let (derived_address, bump_seed) =
                Pubkey::find_program_address(&[new_program_id.as_ref()], program_id);
            if derived_address != programdata_key {
                ic_logger_msg!(log_collector, "ProgramData address is not derived");
                return Err(InstructionError::InvalidArgument);
            }

            // Drain the Buffer account to payer before paying for programdata account
            {
                let mut buffer = instruction_context.try_borrow_instruction_account(3)?;
                let mut payer = instruction_context.try_borrow_instruction_account(0)?;
                payer.checked_add_lamports(buffer.get_lamports())?;
                buffer.set_lamports(0)?;
            }

            let owner_id = *program_id;
            let mut instruction = system_instruction::create_account(
                &payer_key,
                &programdata_key,
                1.max(rent.minimum_balance(programdata_len)),
                programdata_len as u64,
                program_id,
            );

            // pass an extra account to avoid the overly strict UnbalancedInstruction error
            instruction
                .accounts
                .push(AccountMeta::new(buffer_key, false));

            invoke_context
                .native_invoke_signed(instruction, &[&[new_program_id.as_ref(), &[bump_seed]]])?;
```

**File:** programs/system/src/system_processor.rs (L160-174)
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

        allocate_and_assign(&mut to, to_address, space, owner, signers, invoke_context)?;
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
