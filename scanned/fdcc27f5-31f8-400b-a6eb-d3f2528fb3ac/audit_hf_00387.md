# [H] multiple times

## Summary
Severity: High
Contest weight: 0.3750
Dataset id: 1773
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _unregisterTrade function, after a trade is partially or fully closed, the open interest reserved for the trade is released: storageT.vaultManager().releaseBalance(_collateral.mul(_trade.leverage)); For a partial trade, _collateral represents the amount of collateral the trader wants to close, while for a full trade close, it equals the initialPosToken of the trade. However, in some cases, when a trader partially closes a trade, any remaining dust collateral is also considered closed. This approach is intended to manage insignificant positions.  
if (_trade.initialPosToken == _collateral || (_collateral + totalFees >= _trade.initialPosToken)){  
storageT.unregisterTrade(_trade.trader, _trade.pairIndex, _trade.index);  
pairInfos.resetTradeInitialAccess(_trade.trader, _trade.pairIndex, _trade.index);  
_collateral = _trade.initialPosToken;  
}  
else {  
storageT.registerPartialTrade(_trade.trader, _trade.pairIndex, _trade.index, _collateral);  
}  
The problem arises because in such cases, the rebalance should consider the complete initialPosToken, not just the provided _collateral for the partial trade. As a result, the open interest corresponding to the remaining part is not released, even though the trade is effectively closed.  
This unreleased open interest accumulates and becomes unrecoverable, compounding the issue due to two factors:  
1. High leverage trades amplify the open interest value that remains stuck.  
2. For large trades where total fees on partial closes are high, the seized collateral is also high. This leads to a significantly higher open interest value being stuck. Due to this LPs would not be able to withdraw funds in some cases as utilisation ratio would go down gradually  
• In TradingCallbacks.sol:554 the releaseBalance function uses incorrect collateral amount when a partial trade is made but full trade is closed  
Internal pre-conditions  
External pre-conditions  
Attack Path  
1. A trader opens a long position in a BTC pair with the following parameters:  
• Collateral: 5000 USDC  
• Leverage: 100x  
• Opening price: 50,000 USDC  
2. Reserved amount = 5000 * 100 = 500,000 USDC  
3. The BTC price then rises to 55,000, allowing the trader to achieve a maximum profit of 500%.  
4. The trader decides to partially close the trade, withdrawing 4600 USDC.  
• Total fees for the partial trade amount to approximately 420 USDC.  
• Rebalance amount = 4600 * 100 = 460,000 USDC  
5. After the partial trade of 4600 USDC, the remaining 400 USDC collateral is less than the total fees of 420 USDC. Therefore, the remaining collateral will also be closed, and the trade will be registered as a full close.  
6. In this scenario, the rebalance should release the full 500,000 USDC, but it only rebalances 460,000 USDC.  
7. As a result, the stuck reserved open interest is:  
stuck reserved open interest = 500,000 - 460,000 = 40,000 USDC  
This causes significant amount of open interest to become unreservable, making it unavailable for other trades. LPs would not be able to withdraw funds as utilisation ratio would go down

## Recommendation
If the trade is converted from partial to full, then release the full amount
