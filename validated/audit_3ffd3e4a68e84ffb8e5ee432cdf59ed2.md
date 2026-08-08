### Title
Global program-disable gate in the ZK ElGamal Proof program blocks `CloseContextState`, freezing user rent-exempt lamports - (File: `programs/zk-elgamal-proof/src/lib.rs`)

### Summary
The `zk-elgamal-proof` builtin program gates its entire entrypoint behind a single feature-controlled "pause" check that returns an error for every instruction — including `CloseContextState` — whenever the program is disabled. This mirrors the reported `LpToken.sol` pattern: a pause mechanism intended to stop new/risky operations (proof verification, context-state creation) is applied indiscriminately to the withdrawal-equivalent path (`CloseContextState`, which returns the account's rent-exempt lamports to its owner), permanently locking user funds in `ProofContextState` accounts for as long as the pause is active.

### Finding Description
The program's `declare_process_instruction!` entrypoint performs a single global check before dispatching to any instruction variant: [1](#0-0) 

```
declare_process_instruction!(Entrypoint, 0, |invoke_context| {
    if invoke_context.get_feature_set().disable_zk_elgamal_proof_program
        && !invoke_context.get_feature_set().reenable_zk_elgamal_proof_program
    {
        ic_msg!(invoke_context, "zk-elgamal-proof program is temporarily disabled");
        return Err(InstructionError::InvalidInstructionData);
    }
    ...
    match instruction {
        ProofInstruction::CloseContextState => { ... process_close_proof_context(invoke_context) }
        ...
```

`ProofInstruction::CloseContextState` is the sole mechanism a user has to reclaim the rent-exempt lamports held in a `ProofContextState` account they created and own: [2](#0-1) . The check at the top of the entrypoint applies uniformly to `CloseContextState` just as it does to the "deposit-like" verification/creation instructions (`VerifyZeroCiphertext`, `VerifyPubkeyValidity`, etc.). There is no carve-out that still permits users to close their own context-state accounts and recover their lamports while the program is disabled — exactly the class of bug described in the report, where a pause switch meant for deposit-style entry points is also applied to the withdrawal-style exit point.

### Impact Explanation
While `disable_zk_elgamal_proof_program` is active (and `reenable_zk_elgamal_proof_program` is not), any account holding a `ProofContextState` cannot be closed by its owner via the only program-defined path (`CloseContextState`). The lamports funding that account's rent-exemption remain locked in the account, unrecoverable by the legitimate owner, until the feature flags change back. This is a concrete, non-theoretical impact: it happened in production — this program was in fact disabled network-wide via `disable_zk_elgamal_proof_program` due to a bug, and later reactivated via `reenable_zk_elgamal_proof_program`, demonstrating that during any such disablement window every `ProofContextState` account's rent-exempt SOL is inaccessible to its rightful owner.

### Likelihood Explanation
The condition triggers deterministically whenever the disable feature is active without the re-enable feature also being active — the same governance state that has already occurred historically for this program. Any user who created a `ProofContextState` account prior to (or during) such a window is affected; no additional user action or attacker capability is required beyond having previously interacted with the program, which is a normal unprivileged use case (confidential transfers / ZK proof verification flows).

### Recommendation
Scope the "program disabled" gate to only the state-mutating/entry instructions that create new proof-context liabilities (e.g., `VerifyZeroCiphertext`, `VerifyCiphertextCiphertextEquality`, and the other `Verify*` variants that create `ProofContextState` accounts), and exempt `CloseContextState` from the disable check so that users can always reclaim their rent-exempt lamports regardless of the program's pause state — mirroring the report's recommendation to keep pausable behavior on deposit paths only, never on withdrawal/exit paths.

### Proof of Concept
1. Activate `disable_zk_elgamal_proof_program` cluster-wide (or simulate via `mock_process_instruction_with_feature_set` with that feature enabled and `reenable_zk_elgamal_proof_program` disabled), matching the entrypoint check at `programs/zk-elgamal-proof/src/lib.rs:176-182`.
2. Have a user submit `ProofInstruction::CloseContextState` for a `ProofContextState` account they own (created before the pause).
3. Observe the instruction returns `InstructionError::InvalidInstructionData` before even reaching `process_close_proof_context`, so `destination_account.checked_add_lamports(...)` at `programs/zk-elgamal-proof/src/lib.rs:167` never executes.
4. The account's rent-exempt lamports remain stuck in the `ProofContextState` account for the duration of the pause, with no alternative program instruction able to release them.

### Citations

**File:** programs/zk-elgamal-proof/src/lib.rs (L132-173)
```rust
fn process_close_proof_context(invoke_context: &mut InvokeContext) -> Result<(), InstructionError> {
    let transaction_context = &invoke_context.transaction_context;
    let instruction_context = transaction_context.get_current_instruction_context()?;

    let owner_pubkey = {
        if !instruction_context.is_instruction_account_signer(2)? {
            return Err(InstructionError::MissingRequiredSignature);
        }

        *instruction_context.get_key_of_instruction_account(2)?
    };

    let proof_context_account_pubkey = *instruction_context.get_key_of_instruction_account(0)?;
    let destination_account_pubkey = *instruction_context.get_key_of_instruction_account(1)?;
    if proof_context_account_pubkey == destination_account_pubkey {
        return Err(InstructionError::InvalidInstructionData);
    }

    let mut proof_context_account = instruction_context.try_borrow_instruction_account(0)?;
    if *proof_context_account.get_owner() != id() {
        return Err(InstructionError::InvalidAccountOwner);
    }
    let proof_context_state_meta =
        ProofContextStateMeta::try_from_bytes(proof_context_account.get_data())?;
    if proof_context_state_meta.proof_type == ProofType::Uninitialized.into() {
        return Err(InstructionError::UninitializedAccount);
    }

    let expected_owner_pubkey = proof_context_state_meta.context_state_authority;

    if owner_pubkey != expected_owner_pubkey {
        return Err(InstructionError::InvalidAccountOwner);
    }

    let mut destination_account = instruction_context.try_borrow_instruction_account(1)?;
    destination_account.checked_add_lamports(proof_context_account.get_lamports())?;
    proof_context_account.set_lamports(0)?;
    proof_context_account.set_data_length(0)?;
    proof_context_account.set_owner(system_program::id().as_ref())?;

    Ok(())
}
```

**File:** programs/zk-elgamal-proof/src/lib.rs (L175-188)
```rust
declare_process_instruction!(Entrypoint, 0, |invoke_context| {
    if invoke_context
        .get_feature_set()
        .disable_zk_elgamal_proof_program
        && !invoke_context
            .get_feature_set()
            .reenable_zk_elgamal_proof_program
    {
        ic_msg!(
            invoke_context,
            "zk-elgamal-proof program is temporarily disabled"
        );
        return Err(InstructionError::InvalidInstructionData);
    }
```
