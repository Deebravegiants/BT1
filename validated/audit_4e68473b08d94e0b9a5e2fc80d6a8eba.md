This confirms `cpi_bytes_per_unit` is entirely sourced from `SVMTransactionExecutionCost` (a runtime-constant struct), and the only user-settable compute-budget fields are `requested_heap_size`, `requested_compute_unit_limit`, `requested_compute_unit_price`, and `requested_loaded_accounts_data_size_limit` via `ComputeBudgetInstructionDetails::process_instruction` — none of which touch `cpi_bytes_per_unit`.

### Title
No vulnerability — `cpi_bytes_per_unit` is a fixed runtime constant not reachable or settable by any user transaction field - (File: syscalls/src/mem_ops.rs)

### Summary
The `mem_op_consume` function does compute `n.checked_div(compute_cost.cpi_bytes_per_unit).unwrap_or(u64::MAX)`, which would indeed degrade to `u64::MAX` if `cpi_bytes_per_unit` were ever zero [1](#0-0) . However, `cpi_bytes_per_unit` is exclusively populated from `SVMTransactionExecutionCost`, whose only constructor sets it to the fixed literal `250` and there is no other construction path in the codebase [2](#0-1) .

### Finding Description
`ComputeBudget::from_budget_and_cost` copies `cpi_bytes_per_unit` directly from the `SVMTransactionExecutionCost` argument without any transformation [3](#0-2) , and the reverse `to_cost` does the same [4](#0-3) . The only place `SVMTransactionExecutionCost` is constructed is via `Default::default()`, which hardcodes `cpi_bytes_per_unit: 250` [2](#0-1) .

The user-facing compute-budget instruction surface (`ComputeBudgetInstruction::RequestHeapFrame`, `SetComputeUnitLimit`, `SetComputeUnitPrice`, `SetLoadedAccountsDataSizeLimit`) is exhaustively matched in `ComputeBudgetInstructionDetails::process_instruction`, and any other instruction data returns `InvalidInstructionData` [5](#0-4) . None of these four fields feed into `cpi_bytes_per_unit`; `sanitize_and_convert_to_compute_budget_limits` only ever produces `ComputeBudgetLimits { updated_heap_bytes, compute_unit_limit, compute_unit_price, loaded_accounts_bytes }` [6](#0-5) . There is no code path from user transaction data into `SVMTransactionExecutionCost` construction or mutation — it is loaded once per execution environment as a validator-side runtime constant, not derived from any per-transaction or per-account attacker-controlled input.

### Impact Explanation
None. Since `cpi_bytes_per_unit` can never be forced to zero by an unprivileged attacker via any transaction field, instruction, ALT, durable nonce, or account layout, the `unwrap_or(u64::MAX)` fallback in `mem_op_consume` is unreachable in practice on any conforming validator build. This is defense-in-depth code for a case that cannot occur through the sanctioned instruction surface.

### Likelihood Explanation
Not exploitable by an unprivileged attacker. Forcing `cpi_bytes_per_unit == 0` would require validator/operator-side modification of the compiled-in default cost table, which is explicitly out of scope (requires validator/leader/operator config control, not a normal user transaction).

### Recommendation
No fix required for the attacker-reachable path described. If desired as defense-in-depth, `cpi_bytes_per_unit` could be typed as `NonZeroU64` in `SVMTransactionExecutionCost` to make the zero case statically unrepresentable, but this is not a security-relevant change given current construction paths.

### Proof of Concept
Not applicable — no reachable attacker input flows into `cpi_bytes_per_unit`. A confirmatory test would just assert that `ComputeBudgetInstructionDetails::sanitize_and_convert_to_compute_budget_limits` never returns a value affecting `cpi_bytes_per_unit`, and that `SVMTransactionExecutionCost::default().cpi_bytes_per_unit == 250` for all `FeatureSet` variants, matching existing tests such as `test_process_instructions` [7](#0-6) .

### Citations

**File:** syscalls/src/mem_ops.rs (L3-10)
```rust
fn mem_op_consume(invoke_context: &mut InvokeContext, n: u64) -> Result<(), Error> {
    let compute_cost = invoke_context.get_execution_cost();
    let cost = compute_cost.mem_op_base_cost.max(
        n.checked_div(compute_cost.cpi_bytes_per_unit)
            .unwrap_or(u64::MAX),
    );
    invoke_context.compute_meter.consume_checked(cost)
}
```

**File:** program-runtime/src/execution_budget.rs (L207-216)
```rust
impl Default for SVMTransactionExecutionCost {
    fn default() -> Self {
        SVMTransactionExecutionCost {
            log_64_units: 100,
            create_program_address_units: 1500,
            invoke_units: DEFAULT_INVOCATION_COST,
            sha256_base_cost: 85,
            sha256_byte_cost: 1,
            log_pubkey_units: 100,
            cpi_bytes_per_unit: 250, // ~50MB at 200,000 units
```

**File:** compute-budget/src/compute_budget.rs (L170-187)
```rust
    pub fn from_budget_and_cost(
        budget: &SVMTransactionExecutionBudget,
        cost: &SVMTransactionExecutionCost,
    ) -> Self {
        Self {
            compute_unit_limit: budget.compute_unit_limit,
            log_64_units: cost.log_64_units,
            create_program_address_units: cost.create_program_address_units,
            invoke_units: cost.invoke_units,
            max_instruction_stack_depth: budget.max_instruction_stack_depth,
            max_instruction_trace_length: budget.max_instruction_trace_length,
            sha256_base_cost: cost.sha256_base_cost,
            sha256_byte_cost: cost.sha256_byte_cost,
            sha256_max_slices: budget.sha256_max_slices,
            max_call_depth: budget.max_call_depth,
            stack_frame_size: budget.stack_frame_size,
            log_pubkey_units: cost.log_pubkey_units,
            cpi_bytes_per_unit: cost.cpi_bytes_per_unit,
```

**File:** compute-budget/src/compute_budget.rs (L249-257)
```rust
    pub fn to_cost(&self) -> SVMTransactionExecutionCost {
        SVMTransactionExecutionCost {
            log_64_units: self.log_64_units,
            create_program_address_units: self.create_program_address_units,
            invoke_units: self.invoke_units,
            sha256_base_cost: self.sha256_base_cost,
            sha256_byte_cost: self.sha256_byte_cost,
            log_pubkey_units: self.log_pubkey_units,
            cpi_bytes_per_unit: self.cpi_bytes_per_unit,
```

**File:** compute-budget-instruction/src/compute_budget_instruction_details.rs (L147-153)
```rust
        Ok(ComputeBudgetLimits {
            updated_heap_bytes,
            compute_unit_limit,
            compute_unit_price,
            loaded_accounts_bytes,
        })
    }
```

**File:** compute-budget-instruction/src/compute_budget_instruction_details.rs (L155-186)
```rust
    fn process_instruction(&mut self, index: u8, instruction: &SVMInstruction) -> Result<()> {
        let invalid_instruction_data_error =
            TransactionError::InstructionError(index, InstructionError::InvalidInstructionData);
        let duplicate_instruction_error = TransactionError::DuplicateInstruction(index);

        match try_from_slice_unchecked(instruction.data) {
            Ok(ComputeBudgetInstruction::RequestHeapFrame(bytes)) => {
                if self.requested_heap_size.is_some() {
                    return Err(duplicate_instruction_error);
                }
                self.requested_heap_size = Some((index, bytes));
            }
            Ok(ComputeBudgetInstruction::SetComputeUnitLimit(compute_unit_limit)) => {
                if self.requested_compute_unit_limit.is_some() {
                    return Err(duplicate_instruction_error);
                }
                self.requested_compute_unit_limit = Some((index, compute_unit_limit));
            }
            Ok(ComputeBudgetInstruction::SetComputeUnitPrice(micro_lamports)) => {
                if self.requested_compute_unit_price.is_some() {
                    return Err(duplicate_instruction_error);
                }
                self.requested_compute_unit_price = Some((index, micro_lamports));
            }
            Ok(ComputeBudgetInstruction::SetLoadedAccountsDataSizeLimit(bytes)) => {
                if self.requested_loaded_accounts_data_size_limit.is_some() {
                    return Err(duplicate_instruction_error);
                }
                self.requested_loaded_accounts_data_size_limit = Some((index, bytes));
            }
            _ => return Err(invalid_instruction_data_error),
        }
```

**File:** compute-budget-instruction/src/instructions_processor.rs (L61-70)
```rust
    #[test]
    fn test_process_instructions() {
        // Units
        test!(
            &[],
            Ok(ComputeBudgetLimits {
                compute_unit_limit: 0,
                ..ComputeBudgetLimits::default()
            })
        );
```
