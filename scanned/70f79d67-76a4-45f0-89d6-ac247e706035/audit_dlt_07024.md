# [M] M-12 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-23
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/17
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L961-L963


# Vulnerability details

## C4 issue
M-12: [Wrong global lending limit check in _deposit function](https://github.com/code-423n4/2024-03-revert-lend-findings/issues/324)

## Comment
The original code wrongly uses `totalSupply()` to check against `globalLendLimit`, this needs to be converted to assets first:
```solidity
function _deposit(
    address receiver,
    uint256 amount,
    bool isShare,
    bytes memory permitData
) internal returns (uint256 assets, uint256 shares) {
    ...

    _mint(receiver, shares);

    //@audit must convert totalSupply() to assets before comparing with globalLendLimit
    if (totalSupply() > globalLendLimit) {
        revert GlobalLendLimit();
    }

    if (assets > dailyLendIncreaseLimitLeft) {
        revert DailyLendIncreaseLimit();
    } else {
        dailyLendIncreaseLimitLeft -= assets;
    }
    ...
}
```

## Proof of Concept
[PR #16](https://github.com/revert-finance/lend/pull/16) converts the asset
before comparison:
```solidity
        uint256 totalSupplyValue = _convertToAssets(totalSupply(), newLendExchangeRateX96, Math.Rounding.Up);
        if (totalSupplyValue > globalLendLimit) {
            revert GlobalLendLimit();
        }
```
However, this commit [#161 Gas Optimizations](https://github.com/revert-finance/lend/commit/f7aafe4866dd487634dab48357a83fd79bb798f1) reverts this change back to the original code, the comparison part still compare `totalSupply() + shares` against `globalLendLimit`:
```solidity
if (totalSupply() + shares > globalLendLimit) {
            revert GlobalLendLimit();
        }
        if (assets > dailyLendIncreaseLimitLeft) {
            revert DailyLendIncreaseLimit();
        }
```

## Recommended mitigation 
Bring back the change to convert totalSupply to asset before comparison:
```solidity
uint256 totalSupplyValue = _convertToAssets(totalSupply(), newLendExchangeRateX96, Math.Rounding.Up);
        if (totalSupplyValue > globalLendLimit) {
            revert GlobalLendLimit();
        }
```











## Assessed type

Other
