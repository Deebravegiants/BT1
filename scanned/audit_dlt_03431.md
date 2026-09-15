# [H] Loss of funds in `PendleConnector.depositIntoMarket()`

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1363
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/PendleConnector.sol#L112-L119
https://github.com/pendle-finance/pendle-core-v2-public/blob/e48767be54fd668c4ea693ac56d13186f2517e3d/contracts/core/Market/v3/PendleMarketV3.sol#L86-L97
https://github.com/pendle-finance/pendle-core-v2-public/blob/e48767be54fd668c4ea693ac56d13186f2517e3d/contracts/core/Market/v3/PendleMarketV3.sol#L223-L229


# Vulnerability details

## Impact  
`PendleConnector` contracts can lose out on funds when minting LP tokens.  
## Proof of Concept 
The `PendleMarketV3.mint()` function accepts as parameters `uint256 netSyDesire` and `uint256 netPtDesired` , which serve as upper bounds, where the Market will try and mint as many LP tokens as possible such that neither of the upper bound amounts are exceeded. The issue is that in `PendleConnector.depositIntoMarket`, the developers incorrectly assume a call to `PendleMarketV3.skim()` will return back any unused tokens that were sent. The `skim()` function sends the extra tokens to the Pendle treasury rather than the calling contract: [skim()](https://github.com/pendle-finance/pendle-core-v2-public/blob/e48767be54fd668c4ea693ac56d13186f2517e3d/contracts/core/Market/v3/PendleMarketV3.sol#L223-L229).
```solidity
    * @dev skim allows us to get the surplus tokens
    */
function depositIntoMarket(IPMarket market, uint256 SYamount, uint256 PTamount) external onlyManager nonReentrant {
    (IPStandardizedYield _SY, IPPrincipalToken _PT,) = IPMarket(market).readTokens();
    IERC20(address(_SY)).safeTransfer(address(market), SYamount);
    IERC20(address(_PT)).safeTransfer(address(market), PTamount);
    market.mint(address(this), SYamount, PTamount);
    market.skim();
    emit DepositIntoMarket(address(market), SYamount, PTamount);
}
```

## Tools used
Manual Inspection
## Recommended Mitigation Steps
Remove the call to `market.skim()` and integrate with `MarketMathCore.addLiquidity()` to pre-calculate the used `SY` and `PT` amounts which then can be supplied to `market.mint()`. This will ensure no tokens are lost.  


## Assessed type

Context
