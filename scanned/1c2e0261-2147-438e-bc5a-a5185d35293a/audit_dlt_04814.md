# [H] Two addresses token will cause double claim of stake when sponsor series runs settle()

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-sense
Published: 2022-11-11
Source: https://github.com/sherlock-audit/2022-11-sense-judging/issues/31
Type: sherlock-finding

## Details
koxuan

high

# Two addresses token will cause double claim of stake when sponsor series runs settle()

## Summary
 There are tokens with two addresses that exist in the blockchain. Synthetix's `ProxyERC20` contract is one example which is used by sUSD, sETH and more. If yield bearing tokens have two addresses and is being used as target by adapter, this can cause double claim of stake in the event that the two different addresses are used for the stake and target address.
## Vulnerability Detail
`uint256 assetBalPost = asset.balanceOf(address(this));` will  include the stake in the event that stake and target are the same token. However, `       if (stake != address(asset)) ` can be bypassed by a token with two addresses, and therefore allowing the sponsor series to claim the stake again. 




## Impact
Series sponsor will double claim stake from the AutoRoller, causing loss of fund.

## Code Snippet

[AutoRoller.sol#L280-282](https://github.com/sherlock-audit/2022-11-sense/blob/main/contracts/src/AutoRoller.sol#L280-L282)

```solidity
        uint256 assetBalPre = asset.balanceOf(address(this));
        divider.settleSeries(address(adapter), maturity); // Settlement will fail if maturity hasn't been reached.
        uint256 assetBalPost = asset.balanceOf(address(this));
```

[AutoRoller.sol#L287-L289](https://github.com/sherlock-audit/2022-11-sense/blob/main/contracts/src/AutoRoller.sol#L287-L289)
```solidity
        if (stake != address(asset)) {
            ERC20(stake).safeTransfer(msg.sender, stakeSize);
        }
```


## Tool used

Manual Review

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-sense-judging/issues/31_
