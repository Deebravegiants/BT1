## Analysis

The core of the C4 finding is a **griefing/DoS pattern**: an unprivileged attacker can proactively populate an account (or in the GMX case, hold a nonzero balance) that a protocol's migration/state-transition logic requires to be empty/nonexistent, thereby permanently blocking that scheduled migration. Agave has a directly analogous, concretely reachable pattern in its **Core BPF builtin migration** logic, which runs unconditionally in the bank-commit path whenever a builtin's migration feature gate activates.

### Root cause

`TargetBuiltin::new_checked` (and the analogous `TargetBpfV2::new_checked`) gate the migration on the target's deterministic `program_data_address` (`get_program_data_address(program_address)`) being empty. When `allow_prefunded` is `false` (the default unless the `relax_programdata_account_check_migration` feature is active), **any** existing account at that address — even one with a single lamport and owned by the System Program — causes the check to fail with `CoreBpfMigrationError::ProgramHasDataAccount`: [1](#0-0) 

`program_data_address` is fully deterministic and publicly computable by anyone (`get_program_data_address(&program_id)`), and builtin `program_id`s and their migration feature IDs are public well ahead of activation (declared in `builtins/src/lib.rs`), e.g.: [2](#0-1) 

The migration itself is invoked unconditionally on feature activation, inside the bank's per-epoch-boundary commit path, with a mere `warn!` on failure (no retry, no alternate path): [3](#0-2) 

Because sending lamports to *any* address (even one that has never been "created") via a System Program `Transfer` creates the destination account owned by the System Program with the transferred balance, any unprivileged user can send `1` lamport to the known `program_data_address` before the migration feature activates. This satisfies `bank.get_account_with_fixed_root(&program_data_address).is_some()` and permanently blocks that specific migration attempt — exactly analogous to the GMX `signalTransfer` griefing via forced non-zero vester balance.

Notably, agave itself later gates this exact griefing vector behind `relax_programdata_account_check_migration`, which switches to `allow_prefunded = true` and only blocks migration if the account is owned by something *other than* the System Program (which an outside attacker generally cannot arrange for a program-derived address they don't control): [4](#0-3) [5](#0-4) 

This confirms the bug class is real and already recognized as worth mitigating — the mitigation is feature-gated, so until/unless `relax_programdata_account_check_migration` is active on a given cluster, the strict check remains exploitable.

### Title
Builtin-to-Core-BPF migration can be permanently griefed by pre-funding the deterministic `program_data_address` - (File: `runtime/src/bank/builtins/core_bpf_migration/target_builtin.rs`)

### Summary
Agave's Core BPF builtin migration path checks that a program's deterministic `program_data_address` PDA has no existing account before performing the migration. Because this address is publicly computable and can be funded by anyone via an ordinary System Program transfer (which creates an account owned by the System Program), an unprivileged actor can pre-fund the address before a scheduled migration feature activates, causing the check `bank.get_account_with_fixed_root(&program_data_address).is_some()` to be true and the migration to fail with `CoreBpfMigrationError::ProgramHasDataAccount`, mirroring the reported `PirexGmx.initiateMigration` griefing pattern (forcing a required "empty" precondition to be non-empty to block a scheduled state transition).

### Finding Description
`TargetBuiltin::new_checked` and `TargetBpfV2::new_checked` require the target's `program_data_address` to not exist (`allow_prefunded == false` path) or to be owned strictly by the System Program (`allow_prefunded == true` path) before allowing `migrate_builtin_to_core_bpf` / `upgrade_loader_v2_program_with_loader_v3_program` to proceed: [1](#0-0) 

Whether `allow_prefunded` is true or false is itself governed by the `relax_programdata_account_check_migration` feature flag at the call site: [5](#0-4) 

Until that feature is active on a cluster, `allow_prefunded` is `false`, and the strict check applies: *any* pre-existing account at `program_data_address` — including one created by a trivial 1-lamport `SystemInstruction::Transfer` from any unprivileged wallet — blocks the migration. The transfer instruction itself imposes no ownership or signer requirement on the recipient: [6](#0-5) 

The migration attempt itself happens automatically and only once, driven by feature activation inside the bank's epoch-boundary processing, with failure simply logged and silently skipped — there is no retry mechanism built into this code path: [3](#0-2) 

Because `program_id`s of builtins and their migration feature IDs (and therefore the derived `program_data_address`) are all public constants declared ahead of time, e.g. for `bpf_loader_upgradeable_program` and `compute_budget_program`: [7](#0-6) 
any actor can precompute the target address and grief it before the feature activates.

### Impact Explanation
A successful grief permanently prevents that specific scheduled Core BPF migration (e.g., replacing a builtin program like `compute_budget_program` or `bpf_loader_upgradeable_program` with its Core BPF equivalent) from completing on-chain. Since the failure path only logs a warning and does not halt or diverge the bank (all validators compute the same deterministic failure), this is not a consensus-safety bug, but it is a concrete, unprivileged, low-cost denial of a planned protocol upgrade mechanism — the cluster would need to coordinate a brand-new feature gate/buffer address to retry the migration, which is itself a form of operational cost/impact caused entirely by an unprivileged actor.

### Likelihood Explanation
Exploitation requires only a single System Program `Transfer` instruction (any lamport amount) targeting a fully public, deterministic address, executed by any funded account, at any point before the relevant migration feature activates (activation times are known in advance since feature-gate proposals are public). This makes the attack trivially reproducible and cheap, contingent only on `relax_programdata_account_check_migration` not yet being active for the specific migration in question.

### Recommendation
Default `allow_prefunded` to `true` (or otherwise ignore benign System-Program-owned, low-value pre-funding) unconditionally for all Core BPF migrations rather than gating the fix behind `relax_programdata_account_check_migration`, so unprivileged actors cannot use a simple lamport transfer to block a scheduled migration. Alternatively/additionally, sweep or reclaim any pre-existing System-Program-owned balance at `program_data_address` as part of migration rather than treating its mere existence as fatal.

### Proof of Concept
1. Identify an upcoming Core BPF migration's target builtin `program_id` (public, e.g. `compute_budget_program::id()`), and compute `program_data_address = get_program_data_address(&program_id)` (public derivation, see `builtins/src/lib.rs` config and `target_builtin.rs`).
2. Before the corresponding migration feature gate (`config.feature_id`) is activated on the cluster, submit an ordinary `SystemInstruction::Transfer` of 1 lamport from any funded wallet to `program_data_address`. Per `system_processor.rs::transfer_verified`, this succeeds unconditionally and creates a System-Program-owned account at that address: [6](#0-5) 
3. When the migration feature activates at the next epoch boundary, `apply_new_builtin_program_feature_transitions` calls `migrate_builtin_to_core_bpf` with `allow_prefunded = feature_set.relax_programdata_account_check_migration` (false unless that separate feature is also active): [5](#0-4) 
4. `TargetBuiltin::new_checked` sees `bank.get_account_with_fixed_root(&program_data_address).is_some()` and returns `CoreBpfMigrationError::ProgramHasDataAccount`: [8](#0-7) 
5. The migration attempt is skipped and only logged via `warn!`, leaving the builtin un-migrated indefinitely.

### Citations

**File:** runtime/src/bank/builtins/core_bpf_migration/target_builtin.rs (L57-82)
```rust
        let program_data_account_lamports = if allow_prefunded {
            // The program data account should not exist, but a system account with funded
            // lamports is acceptable.
            if let Some(account) = bank.get_account_with_fixed_root(&program_data_address) {
                if account.owner() != &SYSTEM_PROGRAM_ID {
                    return Err(CoreBpfMigrationError::ProgramHasDataAccount(
                        *program_address,
                    ));
                }
                account.lamports()
            } else {
                0
            }
        } else {
            // The program data account should not exist and have zero lamports.
            if bank
                .get_account_with_fixed_root(&program_data_address)
                .is_some()
            {
                return Err(CoreBpfMigrationError::ProgramHasDataAccount(
                    *program_address,
                ));
            }

            0
        };
```

**File:** builtins/src/lib.rs (L203-241)
```rust
    pub mod solana_bpf_loader_upgradeable_program {
        pub mod feature {
            solana_pubkey::declare_id!("oPQbVjgoQ7SaQmzZiiHW4xqHbh4BJqqrFhxEJZiMiwY");
        }
        pub mod source_buffer {
            solana_pubkey::declare_id!("6bTmA9iefD57GDoQ9wUjG8SeYkSpRw3EkKzxZCbhkavq");
        }
        pub mod upgrade_authority {
            solana_pubkey::declare_id!("CuJvJY1K2wx82oLrQGSSWtw4AF7nVifEHupzSC2KEcq5");
        }
        pub const CONFIG: super::CoreBpfMigrationConfig = super::CoreBpfMigrationConfig {
            source_buffer_address: source_buffer::id(),
            upgrade_authority_address: Some(upgrade_authority::id()),
            feature_id: feature::id(),
            migration_target: super::CoreBpfMigrationTargetType::Builtin,
            verified_build_hash: None,
            datapoint_name: "migrate_builtin_to_core_bpf_bpf_loader_upgradeable_program",
        };
    }

    pub mod compute_budget_program {
        pub mod feature {
            solana_pubkey::declare_id!("D39vUspVfhjPVD7EtMJZrA5j1TSMp4LXfb43nxumGdHT");
        }
        pub mod source_buffer {
            solana_pubkey::declare_id!("KfX1oLpFC5CwmFeSgXrNcXaouKjFkPuSJ4UsKb3zKMX");
        }
        pub mod upgrade_authority {
            solana_pubkey::declare_id!("HGTbQhaCXNTbpgpLb2KNjqWSwpJyb2dqDB66Lc3Ph4aN");
        }
        pub const CONFIG: super::CoreBpfMigrationConfig = super::CoreBpfMigrationConfig {
            source_buffer_address: source_buffer::id(),
            upgrade_authority_address: Some(upgrade_authority::id()),
            feature_id: feature::id(),
            migration_target: super::CoreBpfMigrationTargetType::Builtin,
            verified_build_hash: None,
            datapoint_name: "migrate_builtin_to_core_bpf_compute_budget_program",
        };
    }
```

**File:** runtime/src/bank.rs (L6252-6288)
```rust
    fn apply_new_builtin_program_feature_transitions(
        &mut self,
        new_feature_activations: &AHashSet<Pubkey>,
    ) {
        for builtin in BUILTINS.iter() {
            if let Some(feature_id) = builtin.enable_feature_id
                && new_feature_activations.contains(&feature_id)
            {
                self.add_builtin(
                    builtin.program_id,
                    builtin.name,
                    ProgramCacheEntry::new_builtin(
                        self.feature_set.activated_slot(&feature_id).unwrap_or(0),
                        builtin.register_fn,
                    ),
                );
            }

            if let Some(core_bpf_migration_config) = &builtin.core_bpf_migration_config {
                // If the builtin is set to be migrated to Core BPF on feature
                // activation, perform the migration which will remove it from
                // the builtins list and the cache.
                if new_feature_activations.contains(&core_bpf_migration_config.feature_id)
                    && let Err(e) = self.migrate_builtin_to_core_bpf(
                        &builtin.program_id,
                        core_bpf_migration_config,
                        self.feature_set
                            .snapshot()
                            .relax_programdata_account_check_migration,
                    )
                {
                    warn!(
                        "Failed to migrate builtin {} to Core BPF: {}",
                        builtin.name, e
                    );
                }
            };
```

**File:** runtime/src/bank/builtins/core_bpf_migration/target_bpf_v2.rs (L47-74)
```rust
        let program_data_address = get_program_data_address(program_address);

        let program_data_account_lamports = if allow_prefunded {
            // The program data account should not exist, but a system account with funded
            // lamports is acceptable.
            if let Some(account) = bank.get_account_with_fixed_root(&program_data_address) {
                if account.owner() != &SYSTEM_PROGRAM_ID {
                    return Err(CoreBpfMigrationError::ProgramHasDataAccount(
                        *program_address,
                    ));
                }
                account.lamports()
            } else {
                0
            }
        } else {
            // The program data account should not exist and have zero lamports.
            if bank
                .get_account_with_fixed_root(&program_data_address)
                .is_some()
            {
                return Err(CoreBpfMigrationError::ProgramHasDataAccount(
                    *program_address,
                ));
            }

            0
        };
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
