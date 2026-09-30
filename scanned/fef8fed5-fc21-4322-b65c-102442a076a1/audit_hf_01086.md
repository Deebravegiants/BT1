# [M] depositIncentive and incentivizeRecurPool do not verify if the incentiveToken exists

## Summary
Severity: Medium
Contest weight: 0.5939
Dataset id: 4154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function depositIncentive(
    RushIncentiveParams[] calldata params,
    address incentiveToken,
    address recipient
)
    external
    nonReentrant
    returns (uint256 totalIncentiveAmount)
    // ...
    // transfer incentive tokens to this contract
    if (totalIncentiveAmount != 0) {
        // @audit - doesn't use the latest version of solady
        incentiveToken.safeTransferFrom2(msgSender, address(this), totalIncentiveAmount);
    }
    // emit event
    emit DepositIncentive(msgSender, incentiveToken, recipient, params, totalIncentiveAmount);
```
Inside solady's implementation, if there is no return data, the function will always success:
```solidity
function trySafeTransferFrom(address token, address from, address to, uint256 amount)
    internal
    returns (bool success)
    /// @solidity memory-safe-assembly
    assembly {
        let m := mload(0x40) // Cache the free memory pointer.
        mstore(0x60, amount) // Store the `amount` argument.
        mstore(0x40, to) // Store the `to` argument.
        mstore(0x2c, shl(96, from)) // Store the `from` argument.
        mstore(0x0c, 0x23b872dd000000000000000000000000) // `transferFrom(address,address,uint256)`.
        success :=
            and( // The arguments of `and` are evaluated from right to left.
                or(eq(mload(0x00), 1), iszero(returndatasize())), // Returned 1 or nothing.
                call(gas(), token, 0, 0x1c, 0x64, 0x00, 0x20)
            )
        mstore(0x60, 0) // Restore the zero slot to zero.
        mstore(0x40, m) // Restore the free memory pointer.
    }
```
This means that an attacker can provide a non-contract to the functions, and the function will succeed. This is problematic in cases where the incentiveToken is a soon-to-be-created contract with a predictable address, such as a Bunni LP token. For instance, if users want to create a reward pool for staking a Bunni LP with another soon-to-be-created Bunni LP token, the attacker can front-run the operation, provide fake rewards, and disrupt the pool rewards accounting.

## Recommendation
Consider checking the code size of incentiveToken, or simply use the latest version of solady, where the code size is also verified within the library.
