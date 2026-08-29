# [M] GMX LP (GLP) token price is vulnerable to manipulation.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/57
Type: sherlock-finding

## Details
ctf_sec

medium

# GMX LP (GLP) token price is vulnerable to manipulation.

## Summary

GMX LP token (GLP)  price is vulnerable to manipulation 

## Vulnerability Detail

Let us look into how the GLP token price is determined:

```solidity
///@notice returns the price of glp token
///@param state set of all state variables of vault
///@param maximize true to get maximum price and flase to get minimum
///@return glp price in usd
function getGlpPrice(State storage state, bool maximize) external view returns (uint256) {
    return _getGlpPrice(state, maximize);
}

///@notice returns the price of glp token
///@param state set of all state variables of vault
///@param maximize true to get maximum price and flase to get minimum
///@return glp price in usd
function _getGlpPrice(State storage state, bool maximize) private view returns (uint256) {
    uint256 aum = state.glpManager.getAum(maximize);
    uint256 totalSupply = state.glp.totalSupply();

    // price per glp token = (total AUM / total supply)
    return aum.mulDivDown(PRICE_PRECISION, totalSupply * 1e24);
}
```

the GMX LP token price is determined by the total pool asset value in GMX / LP token totalSupply. While there is nothing wrong about this equal and implementation, using the spot price of the LP token like this is  still very vulnerable to manipulation.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/57_
