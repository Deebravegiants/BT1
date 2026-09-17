# [M] Owner can steal funds by using incorrect swapData

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/17
Type: sherlock-finding

## Details
csanuragjain

medium

# Owner can steal funds by using incorrect swapData

## Summary
An owner can call `submit` function with malicious swapData which converts user token to Token B instead of Tel. Since contract is blindly trusting its Tel balance so recipient could get 0 amount 

## Vulnerability Detail
1. Owner calls the `submit` function which does below (swapped token is not TEL)

```solidity
(bool swapResult,) = _aggregator.call{value: msg.value}(swapData);
    require(swapResult, "FeeBuyback: swap transaction failed");
    _telcoin.approve(address(_referral), _telcoin.balanceOf(address(this)));
    require(_referral.increaseClaimableBy(recipient, _telcoin.balanceOf(address(this))), "FeeBuyback: balance was not adjusted");
    return true;
```

2. As we can see swapData is blindly trusted. If swapData is changed to make target swap token to be Token A instead of Tel, then increaseClaimableBy will be done on recipient with 0 amount

3. Also now Admin may use rescueERC20 to get back the tokens

## Impact
Admin can steal funds

## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L77

## Tool used
Manual Review

## Recommendation
Calculate the balance before and after calling `_aggregator.call{value: msg.value}(swapData);` which will ensure that Tel balance has changed
