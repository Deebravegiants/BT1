# [M] attacker can perform malicious transactions

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 19751
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To prevent reentrancy during the safe's execTransaction() function call code use _guardEntries and increase it in the checkTransaction() and decrease it in the checkAfterExecution(). But the logic is wrong and code won't underflow in the checkAfterExecution() if attacker perform reentrancy during the execTransaction().
This is some part of the checkTransaction() and checkAfterExecution() code:
```solidity
function checkTransaction(
    address to,
    uint256 value,
    bytes calldata data,
    Enum.Operation operation,
    uint256 safeTxGas,
    uint256 baseGas,
    uint256 gasPrice,
    address gasToken,
    address payable refundReceiver,
    bytes memory signatures,
    address // msgSender
) external override {
    if (msg.sender != address(safe)) revert NotCalledFromSafe();
    uint256 safeOwnerCount = safe.getOwners().length;
    // ensure that safe threshold is correct
    reconcileSignerCount();
    if (safeOwnerCount < minThreshold) {
        revert BelowMinThreshold(minThreshold, safeOwnerCount);
    }
    // get the tx hash; view function
    bytes32 txHash = safe.getTransactionHash(
        // Transaction info
        to,
        value,
        data,
        operation,
        safeTxGas,
        // Payment info
        baseGas,
        gasPrice,
        gasToken,
        refundReceiver,
        // Signature info
        // We subtract 1 since nonce was just incremented in the parent function
        safe.nonce() - 1 // view function
    );
    uint256 validSigCount = countValidSignatures(txHash, signatures, signatures.length / 65);
    unchecked {
        ++_guardEntries;
    }
}
/// @notice Post-flight check to prevent `safe` signers from removing this contract guard, changing any modules, or changing the threshold
/// @dev Modified from https://github.com/gnosis/zodiac-guard-mod/blob/988ebc7b7c1e352f121a0be5f6ae37e79e47a4541/contracts/ModGuard.sol#L86
function checkAfterExecution(bytes32, bool) external override {
    if (msg.sender != address(safe)) revert NotCalledFromSafe();
    // leave checked to catch underflows triggered by re-erntry attempts
    --_guardEntries;
}
```
As you can see code increase the value of the _guardEntries in the checkTransaction() which is called before the transaction execution and decrease its value in the checkAfterExecution which is called after transaction execution. This won't protect against reentrancy during the safe's execTransaction() call. Attacker can perform this actions:
1. Transaction1 which has valid number of signers and set the value of the guard to 0x0. and call safe.execTransaction(Transaction2).
2. Transaction2 which reset the value of the guard to HSG address.
3. Now by calling safe.execTransaction(Transaction1) code would first call checkTransaction() and would see the number of the signers is correct and then increase the value of the _guardEntries to 1 and then code in safe would execute the Transaction1 which would set the guard to 0x0 and execute the Transaction2 in safe.
4. Because guard is 0x0 code would execute the Transaction2 and then during that code would re-set the value of the guard to the HSG address.
5. Now checkAfterExecution() would get executed and would see that guard value is correct and would decrease the _guardEntries.
The attack is possible by changing the value of the threshold in the safe. Because code would perform two increase and one decrease during the reentrancy so the underflow won't happen.
It's possible to set guard or threshold during the execTransaction() and execute another malicious transaction which resets guard and threshold.

## Recommendation
Set the value of the guard to 1 and decrease in the checkTransaction() and increase in the checkAfterExecution().
