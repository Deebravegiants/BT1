# [M] [Tomo-M5] No success check for _refundGas

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/69
Type: sherlock-finding

## Details
Tomo

medium

# [Tomo-M5] No success check for _refundGas

## Summary

No success check for _refundGas

## Vulnerability Detail

In the `_refundGas()` there is no check for external call success or not.

It is possible that the user has confirmed the refunded state, and executed the function, but they are not refunded. 

It is true that there is no check `NounsDAOLogicV2.sol` as well but this is not mentioned in the documentation. 

Therefore, this is a medium-severity bug that can cause unexpected losses to the user.

## Impact

Users can’t be refunded gas fees if the state of refund is true.

## Code Snippet
https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/utils/Refundable.sol#L20-L42
``` solidity
/// @notice Calculate the amount spent on gas and send that to msg.sender from the contract's balance
/// @param _startGas gasleft() at the start of the transaction, used to calculate gas spent
/// @dev Forked from NounsDAO: https://github.com/nounsDAO/nouns-monorepo/blob/master/packages/nouns-contracts/contracts/governance/NounsDAOLogicV2.sol#L1033-L1046
//@todo refund gas can be reentrancy
function _refundGas(uint256 _startGas) internal {
    unchecked {
        uint256 gasPrice = _min(tx.gasprice, block.basefee + MAX_REFUND_PRIORITY_FEE);
        uint256 gasUsed = _startGas - gasleft() + REFUND_BASE_GAS;
        uint refundAmount = gasPrice * gasUsed;
        
        // If gas fund runs out, pay out as much as possible and emit warning event.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/69_
