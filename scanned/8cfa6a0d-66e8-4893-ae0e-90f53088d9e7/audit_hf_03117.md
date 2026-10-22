# [M] Missing revert keyword

## Summary
Severity: Medium
Contest weight: 0.4105
Dataset id: 17590
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Missing revert keyword in functionDelegateCall bypasses an intended safety check, allowing the function to fail silently. In the helper function functionDelegateCall, there is a check to confirm that the target being called is a contract. if (!isContract(target)) Errors.AddressNotContract; However, there is a typo in the check that is missing the revert keyword. As a result, non-contracts can be submitted as targets, which will cause the delegatecall below to return success (because EVM treats no code as STOP opcode), even though it doesn't do anything. (bool success, ) = target.delegatecall(data); require(success, "CALL_FAILED"); The code doesn't accomplish its intended goal of checking to confirm that only contracts are passed as targets, so delegatecalls can silently fail. Helpers.sol#L66-L73 ```solidity function functionDelegateCall( address target, bytes calldata data ) internal { if (!isContract(target)) Errors.AddressNotContract; (bool success, ) = target.delegatecall(data); require(success, "CALL_FAILED"); } ```

## Recommendation
Add missing revert keyword to L70 of Helpers.sol. if (!isContract(target)) revert Errors.AddressNotContract; Confirmed fix.
