No vulnerability found for this question.

**Reasoning:**

The `state_view_at_version` function is a general-purpose historical/read-only state view constructor and intentionally accepts an arbitrary `version` — this is by design, used for archive queries, view functions, debugging, and simulation, not for actual transaction execution against live custody state. [1](#0-0) 

Critically, the actual multisig approval-counting logic that gates asset transfers — `validate_multisig_transaction` — runs inside the VM during real block execution against the live, current chain state via `borrow_global<MultisigAccount>`, not through any Rust-level `state_view_at_version` call with an attacker-supplied version. [2](#0-1) 

The only unprivileged surfaces that expose an arbitrary `version`/`ledger_version` parameter tied to `state_view_at_version` are the `/view` endpoint (read-only Move view functions, no state mutation, no real approval recording) and `/transactions/simulate` (which requires an invalid/zero signature and never commits to storage, and actually binds to `latest_state_view_poem` at the current ledger tip, not an arbitrary historical version). [3](#0-2) [4](#0-3) 

Neither of these paths can cause a real, committed multisig transaction execution (which mutates owner votes, sequence numbers, and executes the payload) to run against a stale, pre-update version of the owner set. Real execution always reads the `MultisigAccount` resource from the current block's state via the VM's live resolver, so the invariant that approval counting uses the current owner set is preserved for any state-mutating, custody-relevant path. The described proof idea only demonstrates that a read-only historical query (equivalent to querying an archived ledger version) returns historical data, which is expected and does not cross a custody boundary or allow acceptance of a stale-owner-set approval for an actual asset transfer.

### Citations

**File:** storage/storage-interface/src/state_store/state_view/db_state_view.rs (L100-108)
```rust
impl DbStateViewAtVersion for Arc<dyn DbReader> {
    fn state_view_at_version(&self, version: Option<Version>) -> StateViewResult<DbStateView> {
        Ok(DbStateView {
            db: self.clone(),
            version,
            maybe_verify_against_state_root_hash: None,
        })
    }
}
```

**File:** aptos-move/framework/aptos-framework/sources/multisig_account.move (L1328-1353)
```text
    fun validate_multisig_transaction(
        owner: &signer, multisig_account: address, payload: vector<u8>) {
        assert_multisig_account_exists(multisig_account);
        assert_is_owner(owner, multisig_account);
        let sequence_number = last_resolved_sequence_number(multisig_account) + 1;
        assert_transaction_exists(multisig_account, sequence_number);

        if (features::multisig_v2_enhancement_feature_enabled()) {
            assert!(
                can_execute(address_of(owner), multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        }
        else {
            assert!(
                can_be_executed(multisig_account, sequence_number),
                error::invalid_argument(ENOT_ENOUGH_APPROVALS),
            );
        };

        // Count approvals, including the executing owner's implicit vote.
        let (num_approvals, _) = num_approvals_and_rejections(multisig_account, sequence_number);
        if (!has_voted_for_approval(multisig_account, sequence_number, address_of(owner))) {
            num_approvals += 1;
        };
        assert!(num_approvals >= num_signatures_required(multisig_account), error::invalid_argument(ENOT_ENOUGH_APPROVALS));
```

**File:** api/src/view_function.rs (L100-113)
```rust
) -> BasicResultWith404<Vec<MoveValue>> {
    // Retrieve the current state of the chain
    let (ledger_info, requested_version) = context
        .get_latest_ledger_info_and_verify_lookup_version(ledger_version.map(|inner| inner.0))?;

    let state_view = context
        .state_view_at_version(requested_version)
        .map_err(|err| {
            BasicErrorWith404::bad_request_with_code(
                err,
                AptosErrorCode::InternalError,
                &ledger_info,
            )
        })?;
```

**File:** api/src/transactions.rs (L1693-1698)
```rust

        // Simulate transaction
        let state_view = self.context.latest_state_view_poem(&ledger_info)?;
        let (vm_status, output) =
            AptosSimulationVM::create_vm_and_simulate_signed_transaction(&txn, &state_view);
        let version = ledger_info.version();
```
