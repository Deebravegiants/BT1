# [M] EulerStrategy._balanceOf and TrueFiStrategy._balanceOf calculate balance in different ways

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L45-L47
Type: audit-issue

## Details
# EulerStrategy._balanceOf and TrueFiStrategy._balanceOf calculate balance in different ways

## Summary
`EulerStrategy._balanceOf` and `TrueFiStrategy._balanceOf` calculate balance in different ways.

## Vulnerability Detail
`EulerStrategy._balanceOf` [function](https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L45-L47) is not counting USDC(that was accidentaly or no sent to the contract). However this amount also should be counted and distributed among stakers as it is done in `TrueFiStrategy._balanceOf` [function](https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L146). You can see that in `TrueFiStrategy._balanceOf` function USDC amount that strategy has was also added `return want.balanceOf(address(this)) + tfUsdcBalance`.
Same approach is used in `MappleStrategy` [here](https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/MapleStrategy.sol#L139). But not in `CompoundStrategy` and `AaveStrategy`.

This has impact on the stake that user will get during the initial staking or restaking and how much USDC it can redeem from his share. In both cases to calculate share amount `totalTokenBalanceStakers` function is used.

```solidity
function totalTokenBalanceStakers() public view override returns (uint256) {
    return
      token.balanceOf(address(this)) +
      yieldStrategy.balanceOf() +
      sherlockProtocolManager.claimablePremiums();
  }
  ```
As you can see this function depends on `yieldStrategy.balanceOf()` that will calculate balance of all strategies.

## Tool used

Manual Review

## Recommendation
Change `EulerStrategy._balanceOf` function to this.
```solidity
function _balanceOf() internal view override returns (uint256) {
    return want.balanceOf(address(this)) + EUSDC.balanceOfUnderlying(address(this));
  }
  ```
