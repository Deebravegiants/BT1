# [M] Low-level transfer via `call

## Summary
Severity: Medium
Contest weight: 0.1835
Dataset id: 3050
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[TimelockController.sol#L414-L415](https://github.com/code-423n4/2022-03-rolla/blob/a06418c9cc847395f3699bdf684a9ac066651ed7/quant-protocol/contracts/timelock/TimelockController.sol#L414-L415)  

In the `_call()` function in `TimelockController.sol`, a call is executed with the following code:
    
    function _call(
            bytes32 id,
            uint256 index,
            address target,
            uint256 value,
            bytes memory data
        ) private {
            // solhint-disable-next-line avoid-low-level-calls
            (bool success, ) = target.call{value: value}(data);
            require(success, "TimelockController: underlying transaction reverted");

            emit CallExecuted(id, index, target, value, data);
        }

Per the Solidity docs:

“The low-level functions call, delegatecall and staticcall return true as their first return value if the account called is non-existent, as part of the design of the EVM. Account existence must be checked prior to calling if needed.”

Therefore, transfers may fail silently.

## Proof of Concept
Please find the documentation [here](https://docs.soliditylang.org/en/develop/control-structures.html#error-handling-assert-require-revert-and-exceptions).

## Recommendation
Check for the account’s existence prior to transferring.

The TimelockController contract was removed from the protocol.
[RollaProject/quant-protocol#90](https://github.com/RollaProject/quant-protocol/pull/90)
