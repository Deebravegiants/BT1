# [M] If a trader of market order or

## Summary
Severity: Medium
Contest weight: 0.5684
Dataset id: 1776
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol uses the collateral token as USDC. If a trader of market order or limit order is blacklisted for USDC token, closing order is reverted. As a result, the order cannot be closed and the reserved USDC tokens cannot be released forever.  
When the order is closed, the protocol transfers the USDC tokens to trader in the VaultManager._sendUSDCToTrader.  
```solidity
function _sendUSDCToTrader(address _trader, uint _amount) internal {
    //...
    require(storageT.usdc().transfer(_trader, _amount));
    //...
}
```
If a trader who opens the order is USDC blacklisted, closing order will be reverted.  
```solidity
function _unregisterTrade(
    ITradingStorage.Trade memory _trade,
    int _percentProfit,
    uint _collateral,
    uint _feeAmountToken,
    uint _lpFeeToken,
    bool _isPnl
) private returns (uint usdcSentToTrader) {
    //...
    storageT.vaultManager().sendUSDCToTrader(address(storageT), feeAfterRebate - referrerRebate - vaultAllocation);
    //...
}
```
Internal pre-conditions  
None  
External pre-conditions  
1. None  
Attack Path  
None  
If a trader of market order or limit order is blacklisted for USDC token, his order cannot be closed and the reserved USDC tokens cannot be released forever.

## Recommendation
In the _sendUSDCToTrader function, track the amount of tokens to transfer to trader instead of direct transferring to trader. And, add the claim function that the traders claim tracked amount of USDC tokens.
