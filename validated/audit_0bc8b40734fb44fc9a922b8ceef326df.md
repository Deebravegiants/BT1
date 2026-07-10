### Title
Missing Destination-Node Signing-Key Authorization in `conclude_node_migration` Allows Premature Migration Finalization — (File: `crates/contract/src/lib.rs`)

---

### Summary

`conclude_node_migration` is intended to be called exclusively by the **new (destination) node** after it has received keyshares from the backup service. However, the contract only checks that an ongoing migration record exists for the caller's **account ID** (`predecessor_account_id`), not that the caller's **signing key** (`env::signer_account_pk()`) matches the destination node's expected key. Because node migration is implemented as a TLS-key swap under the same NEAR account ID, the old (decommissioned) node — or any party holding its account key — can call `conclude_node_migration` prematurely, before the new node has received keyshares, corrupting participant state.

---

### Finding Description

The migration flow is:

1. **`start_node_migration(destination_node_info)`** — called by the old node's operator; stores the new node's `ParticipantInfo` (TLS key, URL) on-chain.
2. **`conclude_node_migration(keyset)`** — intended to be called by the new node after it has received keyshares; replaces the old node's `ParticipantInfo` with the new node's info in the active participant set.

Because migration is a TLS-key swap (same NEAR `AccountId`, different signing key and TLS key), both the old node and the new node share the same `predecessor_account_id`. The contract's only guard is:

> "Returns an error if no ongoing migration exists for the caller."

This check passes for the old node's account key just as readily as for the new node's account key. The old node also knows the current epoch's `keyset` (it is still a participant), so it can supply a valid `keyset` argument.

The codebase explicitly acknowledges this gap:

> **Future Enhancement**: It may be desirable for the contract to verify that calls to `conclude_node_migration(keyset)` come from the actual onboarding node by checking the transaction signer's public key *(see [#1086](https://github.com/near/mpc/issues/1086))*. This would prevent ill-behaved decommissioned nodes from making spurious migration calls. This would require:
> - Comparing `env::signer_account_pk()` with the public key associated with the participant
> - Including this public key in the TEE attestation [1](#0-0) 

The function is located in the migration-service `impl` block of the contract: [2](#0-1) 

The `start_node_migration` caller check (for comparison) uses `assert_caller_is_signer()` to bind account ID to signing key, but `conclude_node_migration` applies no equivalent binding to the destination node's key: [3](#0-2) 

---

### Impact Explanation

A Byzantine participant (the old/decommissioned node, strictly below signing threshold) calls `conclude_node_migration` before the new node has received keyshares. The contract:

1. Replaces the old node's `ParticipantInfo` (TLS key, URL) with the new node's info in the active participant set.
2. Removes the `OngoingNodeMigration` record.

Result: the new node is now listed as an active participant but holds **no keyshares**. Every signing, resharing, or DKG round that requires this participant's contribution will fail. If the network is operating at exactly the governance threshold, a single such disruption can halt all signing — permanently freezing funds controlled by the MPC network until a resharing is completed.

This is **participant-state manipulation that breaks production safety/accounting invariants** without requiring network-level DoS or operator misconfiguration.

---

### Likelihood Explanation

The scenario is realistic and low-cost:

- Node migration is triggered precisely when the old node's environment is suspect (hardware failure, key rotation, TEE migration). The old node's account key may be compromised at the moment migration is most needed.
- The attacker needs only one NEAR transaction and knowledge of the current `keyset` (public on-chain).
- The attack window is the entire duration between `start_node_migration` and the new node's legitimate call to `conclude_node_migration` — potentially minutes to hours in operational practice.
- The codebase's own issue tracker (#1086) and design doc acknowledge this as an open, unmitigated risk. [1](#0-0) 

---

### Recommendation

Implement the check described in issue #1086: before finalizing the migration, compare `env::signer_account_pk()` against the **destination node's account public key** stored in `destination_node_info` (set during `start_node_migration`). Only the transaction signed by the new node's key should be accepted. This mirrors the pattern already used in `submit_participant_info`, where `env::signer_account_pk()` is bound to the attested `account_public_key` in `ReportDataV1`. [2](#0-1) 

---

### Proof of Concept

1. Operator calls `start_node_migration(destination_node_info)` from the old node's account (`node0.near`), storing the new node's TLS key and URL on-chain.
2. Attacker (holding `node0.near`'s account key — e.g., the decommissioned old node itself, or a party who obtained the key) reads the current `keyset` from contract state (public view call).
3. Attacker calls `conclude_node_migration(keyset)` signed by `node0.near`'s old account key, **before** the new node has fetched keyshares from the backup service.
4. Contract checks: protocol is `Running` ✓, ongoing migration exists for `node0.near` ✓, keyset matches epoch ✓ — call succeeds.
5. The new node's `ParticipantInfo` is now active in the participant set, but the new node has no keyshares.
6. All subsequent signing rounds requiring `node0.near`'s contribution fail. If the network is at threshold, signing halts entirely. [4](#0-3) [2](#0-1)

### Citations

**File:** docs/migration-service.md (L372-395)
```markdown
- **`conclude_node_migration(keyset: &Keyset)`** - Finalizes a node migration:
    - Called by the new node after receiving keyshares from backup service
    - Verifies the provided `keyset` matches the expected key event IDs for this epoch
    - Replaces the old node's `ParticipantInfo` with the new node's info in the current participant set
    - Removes the `OngoingNodeMigration` record
    - Returns an error if the protocol is not in `Running` state
    - Returns an error if no ongoing migration exists for the caller

- **`register_backup_service(backup_service_info: BackupServiceInfo)`** - Registers or updates backup service:
    - Called by the node operator
    - Stores the backup service's public key and URL for the node operator's account
    - Defines or overrides the `BackupServiceInfo` for the node operator
    - Can be called in any protocol state (`Running`, `Initializing`, or `Resharing`)
    - Returns an error if caller is not a current participant

> **Hard Launch Extension (Planned):** For hard launch, `register_backup_service()` will require an `attestation` and `operator_account_pk` parameter. The contract will verify the attestation validity, Docker image hash, and that the `ReportData` includes both the TLS public key and operator's account public key (`SHA3-384(tls_public_key || operator_account_pk)`). This cryptographically binds the backup service TEE to the specific operator, preventing a malicious backup service from registering under a different operator's account. Backup services will need to refresh attestations before expiration.

#### Migration Related Behavior

- The `OngoingNodeMigration` records are automatically cleared when the protocol transitions from `Running` state to `Resharing` or `Initializing` state, effectively cancelling any in-progress migrations.
- **Future Enhancement**: It may be desirable for the contract to verify that calls to `conclude_node_migration(keyset)` come from the actual onboarding node by checking the transaction signer's public key _(see [(#1086)](https://github.com/near/mpc/issues/1086))_. This would prevent ill-behaved decommissioned nodes from making spurious migration calls. This would require:
    - Comparing `env::signer_account_pk()` with the public key associated with the participant (note: this is different from the TLS key currently stored as [`signer_pk`](https://github.com/near/mpc/blob/b5a9d1b2eef4de47d19b66cb25b577da2b897560/crates/contract/src/tee/tee_state.rs#L32) in TEEState)
    - Including this public key in the TEE attestation

```

**File:** crates/contract/src/lib.rs (L2498-2524)
```rust
    pub fn start_node_migration(
        &mut self,
        destination_node_info: dtos::DestinationNodeInfo,
    ) -> Result<(), Error> {
        // TODO(#1163): require a deposit

        let account_id = Self::assert_caller_is_signer();

        log!(
            "start_node_migration: signer={:?}, destination_node_info={:?}",
            account_id,
            destination_node_info
        );
        let ProtocolContractState::Running(running_state) = &self.protocol_state else {
            return Err(errors::InvalidState::ProtocolStateNotRunning.into());
        };

        if !running_state.is_participant_given_account_id(&account_id) {
            return Err(errors::InvalidState::NotParticipant {
                account_id: account_id.clone(),
            }
            .into());
        }
        self.node_migrations
            .set_destination_node_info(account_id, destination_node_info);
        Ok(())
    }
```
