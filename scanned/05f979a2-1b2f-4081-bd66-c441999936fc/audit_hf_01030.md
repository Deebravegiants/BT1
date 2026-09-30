# [M] No way to collect uniswap fees

## Summary
Severity: Medium
Contest weight: 0.3859
Dataset id: 3955
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the mint stage is done an admin calls Bridge::closeMint, this will end the minting stage and divert some funds to initializing a Uniswap pool with a first LP position in Bridge::_mintInitialPosition:
```solidity
(uint256 tokenId, uint256 liquidity, , ) = manager.mint(params);
lpTokenInfo.tokenId = uint80(tokenId);
lpTokenInfo.liquidity = uint128(liquidity);
lpTokenInfo.tickLower = MIN_TICK;
lpTokenInfo.tickUpper = MAX_TICK;
```
Here the position is created and the details are saved. There is however no way to collect the fees that this position will gradually build up from trading happening in the pool.

## Recommendation
Consider implementing a call to NonfungiblePositionManager::collect which can be restricted to Blerb:
