# [H] Incomplete error handling causes execution

## Summary
Severity: High
Contest weight: 0.7859
Dataset id: 19819
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can define callbacks for Deposits/Withdrawals/Orders execution and cancellations. GMX protocol attempts to manage errors during the execution of the callbacks. A user controlled callback can return a specially crafted revert reason that will make the error handling revert. By making the execution and cancelation revert, a malicious actor can game orders and waste keeper gas.

The bug resides in ErrorUtils.getRevertMessage that is called on every callback attempt. Example of deposit callback:
```solidity
try IDepositCallbackReceiver(deposit.callbackContract()).afterDepositExecution{
    gas: deposit.callbackGasLimit()
}(key, deposit) {
} catch (bytes memory reasonBytes) {
    (string memory reason, /* bool hasRevertMessage */) = ErrorUtils.getRevertMessage(reasonBytes);
    emit AfterDepositExecutionError(key, deposit, reason, reasonBytes);
}
// ob/main/gmx-synthetics/contracts/utils/ErrorUtils.sol#L7
```

```solidity
function getRevertMessage(bytes memory result) internal pure returns (string memory, bool) {
    // If the result length is less than 68, then the transaction either panicked or failed silently
    if (result.length < 68) {
        return ("", false);
    }
    bytes4 errorSelector = getErrorSelectorFromData(result);
    // 0x08c379a0 is the selector for Error(string)
    // referenced from https://blog.soliditylang.org/2021/04/21/custom-errors/
    if (errorSelector == bytes4(0x08c379a0)) {
        assembly {
            result := add(result, 0x04)
        }
        return (abi.decode(result, (string)), true);
    }
    // error may be a custom error, return an empty string for this case
    return ("", false);
}
```

As can be seen in the above snippets, the reasonBytes from the catch statement is passed to getRevertMessage which tries to extract the Error(string) message from the revert. The issue is that the data extracted from the revert can be crafted to revert on abi.decode.

I will elaborate: Correct (expected) revert data looks as follows:
1st 32 bytes: 0x000..64 (bytes memory size)
2nd 32 bytes: 0x08c379a0 (Error(string) selector)
3rd 32 bytes: offset to data
4th 32 bytes: length of data
5th 32 bytes: data

abi.decode reverts if the data is not structured correctly. There can be two reasons for revert:
1. if the 3rd 32 bytes (offset to data) is larger than the uint64 (0xffffffffffffffff)
   - Simplified yul: if gt(offset, 0xffffffffffffffff) { revert }
2. if the 3rd 32 bytes (offset to data) is larger than the uint64 of the encoded data, the call will revert
   - Simplified yul: if iszero(slt(add(offset, 0x1f), size)) { revert }

By reverting with the following data in the callback, the getRevertMessage will revert: 0x000....64 0x0x08c379a0...000 0xffffffffffffffff....000 0x000...2 0x4141

There are two impacts that will occur when the error handling reverts:
(1) Orders can be gamed
Since the following callbacks are controlled by the user:
- afterOrderExecution
- afterOrderCancellation
- afterOrderFrozen

The user can decide when to send the malformed revert data and when not. Essentially preventing keepers from freezing orders and from executing orders until it fits the attacker.

There are two ways to game the orders:
1. An attacker can create a risk free order, by setting a long increase order. If the market increases in his favor, he can decide to "unblock" the execution and receive profit. If the market decreases, he can cancel the order or wait for the right timing.
2. An attacker can create a limit order with a size larger than what is available in the pool. The attacker waits for the price to hit and then deposit into the pool to make the transaction work. This method is supposed to be prevented by freezing orders, but since the attacker can make the freezeOrder revert, the scenario becomes vulnerable again.

(2) drain keepers funds
Since exploiting the bug for both execution and cancellation, keepers will ALWAYS revert when trying to execute Deposits/Withdrawals/Orders. The protocol promises to always pay keepers at least the execution cost. By making the execution and cancellations revert the Deposits/Withdrawals/Orders will never be removed from the store and keepers transactions will keep reverting until potentially all their funds are wasted.

## Recommendation
When parsing the revert reason, validate the offsets are smaller than the length of the encoding.
