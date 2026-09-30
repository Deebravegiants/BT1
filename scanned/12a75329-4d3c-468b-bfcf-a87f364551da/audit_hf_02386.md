# [H] Possible Price Manipulation for UniswapPoolHelper::getPrice()/getLpPrice()

## Summary
Severity: High
Contest weight: 0.5868
Dataset id: 12871
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The UniswapPoolHelper contract defines a routine (i.e., getPrice()) to obtain the price of the RDNT token against ETH in the UniswapV2 RDNT-ETH pair. While examining its logic, we notice the price of the RDNT token is possible to be manipulated. To elaborate, we show below the related code snippet of the UniswapPoolHelper contract. Inside wethReserve.mul(decis).div(rdntReserve) (line 105), where the value of wethReserve or rdntReserve is the token amount in the UniswapV2 RDNT-ETH pair. Its manipulation may cause the price of the RDNT token not trustworthy.
```solidity
function getPrice() public view override returns (uint256 priceInEth) {
    IUniswapV2Pair lpToken = IUniswapV2Pair(lpTokenAddr);
    (uint256 reserve0, uint256 reserve1, ) = lpToken.getReserves();
    uint256 wethReserve = lpToken.token0() != address(rdntAddr) ? reserve0 : reserve1;
    uint256 rdntReserve = lpToken.token0() == address(rdntAddr) ? reserve0 : reserve1;
    uint256 decis = 1e8;
    priceInEth = wethReserve.mul(decis).div(rdntReserve);
}
```
Note other routines, i.e., UniswapPoolHelper::getLpPrice() and BalancerPoolHelper::getPrice()/getLpPrice(), share the same issue.

## Recommendation
Revise current execution logic of above-mentioned routines to defensively detect any manipulation attempts.
