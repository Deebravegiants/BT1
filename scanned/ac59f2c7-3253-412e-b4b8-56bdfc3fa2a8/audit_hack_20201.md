# [H] 5.2.2 Deriving price withbalanceOfis dangerous

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** ConnextPriceOracle.sol#L109-L
**Description:** getPriceFromDexderives the price by querying the balance of AMM’s pools.
function getPriceFromDex(address _tokenAddress) public view returns (uint256) {
PriceInfo storage priceInfo = priceRecords[_tokenAddress];
...
uint256 rawTokenAmount = IERC20Extended(priceInfo.token).balanceOf(priceInfo.lpToken);
...
uint256 rawBaseTokenAmount = IERC20Extended(priceInfo.baseToken).balanceOf(priceInfo.lpToken);
...
}

Deriving the price withbalanceOfis dangerous asbalanceOfmay be gamed. Consider univ2 as an example;
Exploiters can first send tokens into the pool and pump the price, then absorb the tokens that were previously
donated by calling mint.
**Recommendation:** Consider querying DEX’s state through function calls such as Univ2’sgetReserves()which
returns the correct state of the pool.
**Connext:** Solved in PR 1649.
**Spearbit:** Verified.
