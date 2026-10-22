# [M] Failure to verify ERC20 function return values in handle_result()

## Summary
Severity: Medium
Contest weight: 0.1647
Dataset id: 8848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The handle_result function in the Erc20Currency implementation is responsible for processing the results of ERC20 contract calls such as transfer and approve. Currently, this function only checks the exit_reason to determine if the EVM call succeeded:
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
However, some ERC20 tokens return a boolean value indicating the success (true) or failure (false) of the operation. By not checking the returned data (value), the function may incorrectly assume that the operation was successful when, in fact, it was not. This oversight can lead to situations where transfers or approvals are considered successful by the system, even though the ERC20 contract has signaled a failure through its return value.

## Recommendation
Modify the handle_result function to check the returned data when its length is non-zero. If the data represents a boolean value, decode it and verify that it is true. If the decoded boolean is false, the function should revert the transaction to prevent misinterpretation of the operation's outcome.
