# [M] RestakeToken function is not permissionless

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-maia
Published: 2023-07-03
Source: https://github.com/code-423n4/2023-05-maia-findings/issues/534
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/uni-v3-staker/UniswapV3Staker.sol#L340-L348
https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/uni-v3-staker/UniswapV3Staker.sol#L373-L374


# Vulnerability details

One of the project assumptions is that anyone can call the `restakeToken` function on someone else's token after the incentive ends (at the start of the new gauge cycle). 

```solidity
File: src/uni-v3-staker/UniswapV3Staker.sol
365:     function _unstakeToken(IncentiveKey memory key, uint256 tokenId, bool isNotRestake) private {
366:         Deposit storage deposit = deposits[tokenId];
367: 
368:         (uint96 endTime, uint256 stakedDuration) =
369:             IncentiveTime.getEndAndDuration(key.startTime, deposit.stakedTimestamp, block.timestamp);
370: 
371:         address owner = deposit.owner;
372: 
373: @>      // anyone can call restakeToken if the block time is after the end time of the incentive
374: @>      if ((isNotRestake || block.timestamp < endTime) && owner != msg.sender) revert NotCalledByOwner();
		
		...
```

This assumption is broken because everywhere the `_unstakeToken` is called, the `isNotRestake` flag is set to `true`, including the [`restakeToken`](https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/uni-v3-staker/UniswapV3Staker.sol#L342) function. Because of that, when the caller is not the `deposit.owner`, the `if` block will evaluate to `true`, and the call will revert with `NotCalledByOwner()` error.

```solidity
File: src/uni-v3-staker/UniswapV3Staker.sol
340:     function restakeToken(uint256 tokenId) external {
341:         IncentiveKey storage incentiveId = stakedIncentiveKey[tokenId];
342: @>      if (incentiveId.startTime != 0) _unstakeToken(incentiveId, tokenId, true);
343: 
344:         (IUniswapV3Pool pool, int24 tickLower, int24 tickUpper, uint128 liquidity) =
345:             NFTPositionInfo.getPositionInfo(factory, nonfungiblePositionManager, tokenId);
346: 
347:         _stakeToken(tokenId, pool, tickLower, tickUpper, liquidity);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-maia-findings/issues/534_
