# [M] The option contract can not interact with pool when their tokenX is different.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/169
Type: sherlock-finding

## Details
hansfriese

medium

# The option contract can not interact with pool when their tokenX is different.

## Summary
BufferBinaryOptions.tokenX can be different from pool's tokenX. In that case the option can not interact with pool, and the protocol will not work.

## Vulnerability Detail
When `BufferBinaryOptions` is created, there is no validation about the tokenX. So `BufferBinaryOptions.tokenX` can be different from `pool.tokenX`.
```solidity
    constructor(
        ERC20 _tokenX,
        ILiquidityPool _pool,
        IOptionsConfig _config,
        IReferralStorage _referral,
        AssetCategory _category,
        string memory _assetPair
    ) ERC721("Buffer", "BFR") {
        tokenX = _tokenX;
        pool = _pool;
        config = _config;
        referral = _referral;
        assetPair = _assetPair;
        assetCategory = _category;
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }
```
In that case, funds will be locked in pool.


## Impact
Protocol will not work if the option contract's tokenX is different from pool's tokenX.

## Code Snippet
https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferBinaryOptions.sol#L46-L61


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/169_
