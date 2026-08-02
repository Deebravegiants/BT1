[1](#0-0)

### Citations

**File:** aptos-move/block-executor/src/txn_last_input_output.rs (L4-14)
```rust
use crate::{
    captured_reads::CapturedReads,
    code_cache_global::{add_module_write_to_module_cache, GlobalModuleCache},
    errors::{ParallelBlockExecutionError, ResourceGroupSerializationError},
    executor_utilities::{materialize_output, Materializer},
    explicit_sync_wrapper::ExplicitSyncWrapper,
    limit_processor::BlockGasLimitProcessor,
    scheduler_wrapper::SchedulerWrapper,
    task::{BeforeMaterializationOutput, ExecutionStatus, TransactionOutput},
    types::ReadWriteSummary,
};
```
