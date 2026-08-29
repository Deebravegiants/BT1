# [H] `PendleConnector` incorrectly sends the redeemed `PT` tokens to the market instead of the 

## Summary
Severity: High
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1339
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/PendleConnector.sol#L205


# Vulnerability details

## Impact
Burning a Pendle LP will donate the `PT` tokens to the market instead of withdrawing them to the `PendleConnector` which leads to a loss of funds for the Connector.   
## Proof of Concept  
The Pendle Market `burn()` function accepts as the first address parameter the receiver of the `SY` tokens and a second address parameter that is the receiver of the `PT` tokens. The issue is that in `PendleConnecotr.burnLP()`, the function `market.burn()`  selects the `market` as the receiver of the `PT ` tokens, where it should be the `PendleConnector` i.e., `address(this)`:
```solidity
function burnLP(IPMarket market, uint256 amount) external onlyManager nonReentrant {
	IERC20(address(market)).safeTransfer(address(market), amount);
	// @audit -> address(market) should be address(this)
	market.burn(address(this), address(market), amount);
	market.skim();
	emit BurnLP(address(market), amount);
}
```
```solidity
// PendleMarket.burn()
function burn(
	address receiverSy,
	address receiverPt,
	uint256 netLpToBurn
) external nonReentrant returns (uint256 netSyOut, uint256 netPtOut) {
```

## Tools used
Manual Inspection
## Recommended Mitigation Steps
```diff
    function burnLP(IPMarket market, uint256 amount) external onlyManager nonReentrant {
        IERC20(address(market)).safeTransfer(address(market), amount);
-       market.burn(address(this), address(market), amount);
+       market.burn(address(this), address(this), amount);
        market.skim();
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1339_
