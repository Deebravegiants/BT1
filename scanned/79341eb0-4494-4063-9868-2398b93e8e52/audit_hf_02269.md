# [M] Improper Increase Position Execution Logic in OrderManager

## Summary
Severity: Medium
Contest weight: 0.4599
Dataset id: 12429
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The created increase order requests may be executed by authorized entities, i.e., onlyPositionKeeper. In the process of reviewing the execution of these increase position requests, we notice the current execution logic should be improved. In the following, we show the implementation of the affected executeIncreasePositions() routine. As the name indicates, this routine is designed to batch-execute the created increase position requests. It has a rather straightforward logic in iterating each request for the attempted execution. If the execution is not successful, it aims to cancel the request. If the cancel also fails, the current logic simply deletes the request from the recorded increasePositionRequestKeys array. We argue that the request deletion upon the cancellation failure is not appropriate as it still does not refund the user funds!
```solidity
function executeIncreasePositions(
    uint256 _endIndex,
    address payable _executionFeeReceiver
) external override onlyPositionKeeper {
    uint256 index = increasePositionRequestKeysStart;
    uint256 length = increasePositionRequestKeys.length;
    if (index >= length) {
        return;
    }
    if (_endIndex > length) {
        _endIndex = length;
    }
    while (index < _endIndex) {
        bytes32 key = increasePositionRequestKeys[index];
        // if the request was executed then delete the key from the array
        // if the request was not executed then break from the loop, this can happen if the minimum number of blocks has not yet passed
        // an error could be thrown if the request is too old or if the slippage
        // higher than what the user specified, or if there is insufficient liquidity for the position
        // in case an error was thrown, cancel the request
        try this.executeIncreasePosition(key, _executionFeeReceiver) returns (bool _wasExecuted) {
            if (!_wasExecuted) {
                break;
            }
        } catch {
            // wrap this call in a try catch to prevent invalid cancels from blocking the loop
            try this.cancelIncreasePosition(key, _executionFeeReceiver) returns (bool _wasCancelled) {
                if (!_wasCancelled) {
                    break;
                }
            } catch {}
            delete increasePositionRequestKeys[index];
            index++;
        }
    }
    increasePositionRequestKeysStart = index;
}
```

## Recommendation
Revise the above routine to properly refund user funds when the request cancellation also fails.
