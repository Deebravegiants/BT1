# [M] Unbounded memory growth via EVM Error message allocations

## Summary
Severity: Medium
Contest weight: 0.2425
Dataset id: 8849
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In executor.rs, the EVM error handling code creates permanent memory allocations for each unique error value through the use of Box::leak. While these are not traditional memory leaks from dropping references, they represent a security risk through unbounded memory growth:
fn handle_result(result: CallResult) -> DispatchResult {
    let (exit_reason, value) = result;
    match exit_reason {
        ExitReason::Succeed(ExitSucceed::Returned) => Ok(()),
        ExitReason::Succeed(ExitSucceed::Stopped) => Ok(()),
        _ => Err(DispatchError::Other(&*Box::leak(
            format!("evm:0x{}", hex::encode(value)).into_boxed_str(),
        ))),
    }
}
Each unique error value creates a new permanent memory allocation because:
- The error value is hex encoded (hex::encode(value))
- This creates a new string for each unique value
- Box::leak makes this allocation permanent
- The memory cannot be freed during runtime
An attacker could exploit this by:
- Generating transactions that cause EVM errors
- Ensuring each error has unique data (e.g. ERC20 impl that returned counter++ error everytime transfer is called)
- Each unique error consumes additional memory
- Memory usage grows linearly with unique errors
Example attack pattern:
// Each creates a permanent allocation
tx1 -> error [1,2,3] -> "evm:0x010203"
tx2 -> error [1,2,4] -> "evm:0x010204"
tx3 -> error [1,2,5] -> "evm:0x010205"
// Memory grows with each unique error
The severity is critical because:
- Memory growth is unbounded
- Allocations are permanent for the node's lifetime
- Affects all network nodes
- Could be used as DoS vector
- Memory cannot be reclaimed without node restart

## Recommendation
Use static error messages without dynamic data (recommended):
const EVM_ERROR: &'static str = "EVM execution error";
fn handle_result(result: CallResult) -> DispatchResult {
    let (exit_reason, value) = result;
    match exit_reason {
        ExitReason::Succeed(ExitSucceed::Returned) => Ok(()),
        ExitReason::Succeed(ExitSucceed::Stopped) => Ok(()),
        _ => {
            // Log error details separately if needed
            log::error!("EVM error: 0x{}", hex::encode(&value));
            Err(DispatchError::Other(EVM_ERROR))
        }
    }
}
Implement a bounded error cache (e.g. BTreeMap). The recommended approach is option 1, as it:
- Completely eliminates the memory growth vector
- Maintains error logging capability
- Is simple to implement and maintain
- Has no performance overhead
