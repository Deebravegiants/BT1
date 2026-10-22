# [H] Lost Funds Due To Specifying Wrong ETH Address In completeQueuedWithdrawal

## Summary
Severity: High
Contest weight: 0.8827
Dataset id: 14462
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Specifying a token from another queued withdrawal while withdrawing from beaconChainETHStrategy results in accounting errors that prevents the completion of that queued withdrawal.
EigenLayer’s DelegationManager::completeQueuedWithdrawal() function takes in an array of tokens that correspond to all the strategies that are being withdrawn from. These token addresses are checked to ensure that they match with the strategy in StrategyBase::_beforeWithdrawal():
```solidity
function _beforeWithdrawal(address recipient, IERC20 token, uint256 amountShares) internal virtual {
    require(token == underlyingToken, "StrategyBase.withdraw: Can only withdraw the strategy token");
}
```
These token addresses are also used in Renzo to decrement the queuedShares mapping for each corresponding token in OperatorDelegator::completeQueuedWithdrawal():
```solidity
for (uint256 i; i < tokens.length; ) {
    if (address(tokens[i]) == address(0)) revert InvalidZeroInput();
    // deduct queued shares for tracking TVL
    queuedShares[address(tokens[i])] -= withdrawal.shares[i];
}
```
However, EigenLayer ignores the provided token address when withdrawing from the beaconChainETHStrategy, allowing the ETH withdrawal to complete with any token address as input. This allows a native ETH restake admin through malicious intent or user error to decrement the queued shares of another queued withdrawal token instead, resulting in an underﬂow error that would prevent further token withdrawal of that token type from being completed, and hence causing the withdrawn funds to be irrecoverably lost.

## Recommendation
Consider adding the following check to make sure that only the IS_NATIVE address can be used for beaconChainETHStrategy withdrawals:
```solidity
if (address(tokens[i]) != IS_NATIVE) {
    if (withdrawal.strategies[i] == delegationManager.beaconChainETHStrategy()) {
        revert IncorrectStrategy();
    }
}
```
Restaking Smart Contract Review
