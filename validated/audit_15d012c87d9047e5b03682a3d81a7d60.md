[1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** aptos-move/block-executor/src/txn_last_input_output.rs (L492-510)
```rust
    // Called when a transaction is committed to materialize its recorded output:
    // resource group updates are finalized and serialized, and delayed field
    // identifiers are replaced with committed values in resource writes and events.
    //
    // !!! [CAUTION] !!!: This finalizes the output and may not be concurrent with
    // any other accesses to the output (e.g. querying the write-set, events, etc),
    // as these read accesses are not synchronized and assumed to have terminated.
    pub(crate) fn materialize<M: Materializer<T>>(
        &self,
        txn_idx: TxnIndex,
        materializer: &M,
    ) -> Result<(O::CommittedOutput, Trace), PanicOr<ResourceGroupSerializationError>> {
        with_success_or_skip_rest!(
            self,
            txn_idx,
            |mut t| materialize_output(t, materializer),
            Err(code_invariant_error("[BlockSTM]: Output must be recorded after execution").into())
        )
    }
```

**File:** aptos-move/block-executor/src/errors.rs (L16-28)
```rust
// This is separate error because we need to match the error variant to provide a specialized
// fallback logic if a resource group serialization error occurs.
#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ResourceGroupSerializationError;

#[derive(Clone, Debug, PartialEq, Eq)]
/// Logging is bottlenecked in constructors.
pub(crate) enum SequentialBlockExecutionError<E> {
    // This is separate error because we need to match the error variant to provide a specialized
    // fallback logic if a resource group serialization error occurs.
    ResourceGroupSerializationError,
    ErrorToReturn(BlockExecutionError<E>),
}
```
