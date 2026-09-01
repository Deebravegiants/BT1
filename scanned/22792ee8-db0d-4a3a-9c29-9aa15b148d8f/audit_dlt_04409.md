# [M] use safetansfer()

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-sentiment
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-11-sentiment-judging/issues/14
Type: sherlock-finding

## Details
8olidity

medium

# use safetansfer()

## Summary
use safetansfer()
## Vulnerability Detail
Use secure `safetransfer()` instead of `transfer()`

## Impact
use safetansfer()
## Code Snippet
https://github.com/sherlock-audit/2022-11-sentiment/blob/main/protocol-merged/src/core/Account.sol#L167
```solidity
	// protocol-merged/protocol/src/core/Account.sol
    function sweepTo(address toAddress) external accountManagerOnly {
        uint assetsLen = assets.length;
        for(uint i; i < assetsLen; ++i) {
            try IERC20(assets[i]).transfer(
                toAddress, assets[i].balanceOf(address(this))
            ) {} catch {}
            if (assets[i].balanceOf(address(this)) == 0)
                hasAsset[assets[i]] = false;
        }
        delete assets;
        toAddress.safeTransferEth(address(this).balance);
    }
```
## Tool used

Manual Review

## Recommendation
use safetansfer()
