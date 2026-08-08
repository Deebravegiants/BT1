## Title
Unchecked multiplication in fee-burn calculation can panic/overflow with attacker-controlled `transaction_fee` - (File: `runtime/src/bank/fee_distribution.rs`)

### Summary
`Bank::calculate_reward_and_burn_fee_details` computes the amount of the transaction fee to burn using a raw (non-saturating, non-checked) multiplication and division:

```rust
let burn = fee_details.transaction_fee * self.burn_percent() / 100;
``` [1](#0-0) 

Every other arithmetic operation in this same file and in the surrounding fee/reward-accounting code paths (`deposit_fees`, `deposit_or_burn_fee`, `collector_type_checked`) consistently uses `saturating_add`/`saturating_sub`/`checked_add_lamports`, showing this is an established convention that was skipped here. [2](#0-1) 

### Finding Description
`transaction_fee` inside `CollectorFeeDetails`/`FeeDetails` is derived from `solana_fee::calculate_fee_details`, which sums signature-related fees via `saturating_mul`/`saturating_add` and can legitimately reach values close to `u64::MAX` (e.g., via crafted signature counts or a compute-unit price that saturates the prioritization fee to `u64::MAX`, as shown by `get_prioritization_fee`'s explicit `.unwrap_or(u64::MAX)` fallback). [3](#0-2) [4](#0-3) 

`calculate_reward_and_burn_fee_details` is invoked on every transaction that pays a fee, during bank commit (`calculate_fee_for_traced_transaction`/`deposit_or_burn_fee` path) to determine how much of the fee is burned vs. deposited to the collector: [5](#0-4)  and it is also called from `core/src/transaction_priority.rs` and `core/src/forwarding_stage.rs` for prioritization/estimation purposes, both of which are on the hot path for every transaction the leader schedules or forwards. [6](#0-5) [7](#0-6) 

Since `burn_percent()` is a constant 50 [8](#0-7) , `fee_details.transaction_fee * 50` will overflow `u64` once `transaction_fee` exceeds `u64::MAX / 50` (~3.69 × 10^17). In debug/test builds (and any release build compiled with `overflow-checks = true`, which is not set anywhere in this repo's Cargo profiles based on search), this multiplication would panic with "attempt to multiply with overflow." I did not find an explicit `overflow-checks` setting in the workspace, meaning the default per Rust/Cargo semantics applies (checks off in `--release`, on in debug); this means the practical outcome depends on the exact build/profile used to compile the validator binary, which I could not fully confirm from the index.

### Impact Explanation
- If overflow checks are active for the compiled binary (debug builds, or any release build with `overflow-checks = true`), an attacker who can get a transaction with a sufficiently large `transaction_fee` (achievable via extreme `compute_unit_price` inputs that saturate the prioritization fee to `u64::MAX`) into a bank's commit path would cause the validator to panic inside bank processing — a liveness/halt issue on any node that processes or replays that block.
- If overflow checks are inactive (typical release default), the multiplication silently wraps, producing an incorrect `burn` value. Because `deposit` is computed as `priority_fee.saturating_add(transaction_fee.saturating_sub(burn))`, a wrapped (much smaller or larger) `burn` value directly changes how many lamports are deposited to the collector vs. burned — this is a fee-accounting correctness issue (value moved to/from the wrong destination) reachable purely by an unprivileged user crafting an extreme-fee transaction.

### Likelihood Explanation
Reaching `transaction_fee` near `u64::MAX / 50` requires an extreme compute-unit price/limit combination; `get_prioritization_fee` is explicitly designed to saturate to `u64::MAX` rather than overflow [4](#0-3) , indicating the authors anticipated adversarial extreme fee values in this exact computation chain — but the burn-percent step downstream was not hardened with the same rigor. The fee payer would still need sufficient balance to cover such a fee for the transaction to be processed normally in `validate_fee_payer`, which uses checked arithmetic and would reject it if the payer can't afford it [9](#0-8) , but the vulnerable multiplication is also independently reachable from the estimation/priority path used during banking/forwarding (`calculate_priority_and_cost`/`calculate_priority`) where similar large synthetic fee values can be constructed for cost-estimation purposes without a real balance check gating it.

### Recommendation
Replace the raw multiplication/division with checked or saturating equivalents, consistent with the rest of the file:
```rust
let burn = (fee_details.transaction_fee as u128 * self.burn_percent() as u128 / 100) as u64;
```
or use `checked_mul`/`saturating_mul` on `u64` followed by a safe division, returning/logging an error/clamped value on potential overflow, matching the pattern already used for `checked_add_lamports` and `saturating_add` elsewhere in this file.

### Proof of Concept
1. Construct a transaction whose `SignatureCounts`/`ComputeBudgetInstruction::set_compute_unit_price` combination drives `solana_fee::calculate_fee_details`'s `transaction_fee` (signature fee) or the overall `FeeDetails.total_fee()` close to `u64::MAX` (bounded by `lamports_per_signature` and signature count, or by directly constructing a `CollectorFeeDetails`/`FeeDetails` with an extreme `transaction_fee` for the estimation path in `core/src/transaction_priority.rs`/`forwarding_stage.rs`).
2. Call `Bank::calculate_reward_and_burn_fee_details` (directly reachable via `calculate_fee_for_traced_transaction` in the commit path, or via `calculate_priority_and_cost` in banking/forwarding) with a `transaction_fee` value `> u64::MAX / 50`.
3. Observe: in a debug/overflow-checked build, the process panics at `fee_details.transaction_fee * self.burn_percent() / 100`; in a wrapping build, `burn` silently becomes an incorrect small/large value, causing miscalculated `deposit` (fee-collector) vs. burned lamports.

### Citations

**File:** runtime/src/bank/fee_distribution.rs (L80-106)
```rust
        &self,
        transaction: &impl TransactionWithMeta,
        transaction_configuration: &TransactionConfiguration,
    ) -> u64 {
        let fee_details = solana_fee::calculate_fee_details(
            transaction,
            self.fee_structure().lamports_per_signature,
            transaction_configuration.priority_fee_lamports,
            self.fee_features(),
        );
        let FeeDistribution {
            deposit: reward,
            burn: _,
        } = self.calculate_reward_and_burn_fee_details(&CollectorFeeDetails::from(fee_details));
        reward
    }

    pub fn calculate_reward_and_burn_fee_details(
        &self,
        fee_details: &CollectorFeeDetails,
    ) -> FeeDistribution {
        let burn = fee_details.transaction_fee * self.burn_percent() / 100;
        let deposit = fee_details
            .priority_fee
            .saturating_add(fee_details.transaction_fee.saturating_sub(burn));
        FeeDistribution { deposit, burn }
    }
```

**File:** runtime/src/bank/fee_distribution.rs (L108-115)
```rust
    const fn burn_percent(&self) -> u64 {
        // NOTE: burn percent is statically 50%, in case it needs to change in the future,
        // burn_percent can be bank property that being passed down from bank to bank, without
        // needing fee-rate-governor
        static_assertions::const_assert!(solana_fee_calculator::DEFAULT_BURN_PERCENT <= 100);

        solana_fee_calculator::DEFAULT_BURN_PERCENT as u64
    }
```

**File:** runtime/src/bank/fee_distribution.rs (L182-213)
```rust
    // Deposits fees into a specified account and if successful, returns the new balance of that account
    fn deposit_fees(&self, collector_id: &Pubkey, fees: u64) -> Result<u64, DepositFeeError> {
        let mut account = self
            .get_account_with_fixed_root_no_cache(collector_id)
            .unwrap_or_default();

        let feature_snapshot = self.feature_set.snapshot();
        if feature_snapshot.custom_commission_collector {
            let pre_lamports = account.lamports();
            account
                .checked_add_lamports(fees)
                .map_err(|_| DepositFeeError::LamportOverflow)?;
            if collector_id != &self.leader.vote_address {
                Bank::collector_type_checked(
                    collector_id,
                    pre_lamports,
                    &account,
                    &self.reserved_account_keys,
                    &self.rent_collector().rent,
                    feature_snapshot.relax_post_exec_min_balance_check,
                )?;
            }
        } else {
            if !system_program::check_id(account.owner()) {
                return Err(DepositFeeError::InvalidAccountOwner);
            }

            let pre_balance = account.lamports();
            let distribution = account.checked_add_lamports(fees);
            if distribution.is_err() {
                return Err(DepositFeeError::LamportOverflow);
            }
```

**File:** fee/src/lib.rs (L41-56)
```rust
/// Calculate fees from signatures.
pub fn calculate_signature_fee(
    SignatureCounts {
        num_transaction_signatures,
        num_ed25519_signatures,
        num_secp256k1_signatures,
        num_secp256r1_signatures,
    }: SignatureCounts,
    lamports_per_signature: u64,
) -> u64 {
    let signature_count = num_transaction_signatures
        .saturating_add(num_ed25519_signatures)
        .saturating_add(num_secp256k1_signatures)
        .saturating_add(num_secp256r1_signatures);
    signature_count.saturating_mul(lamports_per_signature)
}
```

**File:** compute-budget/src/compute_budget_limits.rs (L61-69)
```rust
fn get_prioritization_fee(compute_unit_price: u64, compute_unit_limit: u64) -> u64 {
    let micro_lamport_fee: MicroLamports =
        (compute_unit_price as u128).saturating_mul(compute_unit_limit as u128);
    micro_lamport_fee
        .saturating_add(MICRO_LAMPORTS_PER_LAMPORT.saturating_sub(1) as u128)
        .checked_div(MICRO_LAMPORTS_PER_LAMPORT as u128)
        .and_then(|fee| u64::try_from(fee).ok())
        .unwrap_or(u64::MAX)
}
```

**File:** core/src/transaction_priority.rs (L32-53)
```rust
pub(crate) fn calculate_priority_and_cost<Tx: TransactionMeta + SVMStaticMessage>(
    bank: &Bank,
    transaction: &Tx,
    transaction_configuration: &TransactionConfiguration,
) -> (u64, u64) {
    let cost = CostModel::calculate_cost_for_executed_transaction(
        transaction,
        u64::from(transaction_configuration.compute_unit_limit),
        transaction_configuration.loaded_accounts_data_size_limit,
        &bank.feature_set,
    )
    .sum();
    let fee_details = solana_fee::calculate_fee_details(
        transaction,
        bank.fee_structure().lamports_per_signature,
        transaction_configuration.priority_fee_lamports,
        bank.fee_features(),
    );
    let reward = bank
        .calculate_reward_and_burn_fee_details(&CollectorFeeDetails::from(fee_details))
        .get_deposit();

```

**File:** core/src/forwarding_stage.rs (L601-628)
```rust
fn calculate_priority(
    transaction: &RuntimeTransaction<SanitizedTransactionView<&[u8]>>,
    bank: &Bank,
) -> Option<u64> {
    let transaction_configuration = transaction
        .transaction_configuration(&bank.feature_set)
        .ok()?;

    // Manually estimate fee here since currently interface doesn't allow a on SVM type.
    // Doesn't need to be 100% accurate so long as close and consistent.
    let prioritization_fee = transaction_configuration.priority_fee_lamports;
    let signature_details = transaction.signature_details();
    let signature_fee = signature_details
        .total_signatures()
        .saturating_mul(bank.fee_structure().lamports_per_signature);
    let fee_details = FeeDetails::new(signature_fee, prioritization_fee);

    let reward = bank
        .calculate_reward_and_burn_fee_details(&CollectorFeeDetails::from(fee_details))
        .get_deposit();

    let cost = CostModel::estimate_cost(
        transaction,
        transaction.program_instructions_iter(),
        transaction.num_requested_write_locks(),
        &bank.feature_set,
    );

```

**File:** svm/src/account_loader.rs (L373-421)
```rust
pub fn validate_fee_payer(
    payer_account: &mut AccountSharedData,
    payer_index: IndexOfAccount,
    error_metrics: &mut TransactionErrorMetrics,
    rent: &Rent,
    fee: u64,
    relax_post_exec_min_balance_check: bool,
) -> Result<()> {
    if payer_account.lamports() == 0 {
        error_metrics.account_not_found += 1;
        return Err(TransactionError::AccountNotFound);
    }
    let system_account_kind = get_system_account_kind(payer_account).ok_or_else(|| {
        error_metrics.invalid_account_for_fee += 1;
        TransactionError::InvalidAccountForFee
    })?;
    let min_balance = match system_account_kind {
        SystemAccountKind::System => 0,
        SystemAccountKind::Nonce => {
            // Should we ever allow a fees charge to zero a nonce account's
            // balance. The state MUST be set to uninitialized in that case
            rent.minimum_balance(NonceState::size())
        }
    };

    payer_account
        .lamports()
        .checked_sub(min_balance)
        .and_then(|v| v.checked_sub(fee))
        .ok_or_else(|| {
            error_metrics.insufficient_funds += 1;
            TransactionError::InsufficientFundsForFee
        })?;

    let pre_balance = payer_account.lamports();
    payer_account
        .checked_sub_lamports(fee)
        .map_err(|_| TransactionError::InsufficientFundsForFee)?;
    let post_balance = payer_account.lamports();

    check_static_account_rent_state_transition(
        pre_balance,
        post_balance,
        payer_account.data().len(),
        rent,
        payer_index,
        relax_post_exec_min_balance_check,
    )
}
```
