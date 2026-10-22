# [M] D3UserQuote#getUserQuote queries incor-

## Summary
Severity: Medium
Contest weight: 0.5655
Dataset id: 20109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A small typo in the valuation loop of D3UserQuote#getUserQuote uses the wrong variable leading to and incorrect quota being returned. The purpose of a quota is to mitigate risk of positions being too large. This incorrect assumption can dramatically underestimate the quota leading to oversized (and overrisk) positions.
D3UserQuota.sol#L75-L84
```solidity
for (uint256 i = 0; i < tokenList.length; i++) {
    address _token = tokenList[i];
    (address assetDToken,,,,,,,,,,) = d3Vault.getAssetInfo(_token);
    uint256 tokenBalance = IERC20(assetDToken).balanceOf(user);
    if (tokenBalance > 0) {
        tokenBalance = tokenBalance.mul(d3Vault.getExchangeRate(token));
    }
    (uint256 tokenPrice, uint8 priceDecimal) = ID3Oracle(d3Vault._ORACLE_()).getOriginalPrice(_token);
    usedQuota = usedQuota + tokenBalance * tokenPrice / 10 ** (priceDecimal+tokenDecimals);
}
```
D3UserQuota.sol#L80 incorrectly uses token rather than _token as it should. This returns the wrong exchange rate which can dramatically alter the perceived token balance as well as the calculated quota. Quota is calculated incorrectly leading to overly risky positions, which in turn can cause loss to the system

## Recommendation
Change variable from token to _token:
```solidity
tokenBalance = tokenBalance.mul(d3Vault.getExchangeRate(_token));
```
