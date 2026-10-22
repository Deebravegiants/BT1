# [M] Cannot deposit to BathToken if token is Deflationary Token (BathHouse.sol)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-05-rubicon
Published: 2022-05-27
Source: https://github.com/code-423n4/2022-05-rubicon-findings/issues/126
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L136-L203


# Vulnerability details

## Impact
Function `openBathTokenSpawnAndSignal` will alway revert when `newBathTokenUnderlying` or `desiredPairedAsset` is deflationary token 


## Proof of Concept
There are ERC20 tokens that may make certain customizations to their ERC20 contracts.
One type of these tokens is deflationary tokens that charge a certain fee for every ```transfer()``` or ```transferFrom()```
For example, I will assume that `newBathTokenUnderlying` is deflationary token. After [line 163](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L156-L163), the actual amount of `newBathTokenUnderlying` that BathHouse gained will be smaller than `initialLiquidityNew`. It will make the [deposit call](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L168) reverted because there are not enough fund to transfer. 


## Tools Used
Manual review 

## Recommended Mitigation Steps
set `initialLiquidityNew = newBathTokenUnderlying.balanceOf(address(this))`  after [line 163](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L156-L163) and `initialLiquidityExistingBathToken  = desiredPairedAsset.balanceOf(address(this))` after [line 178](https://github.com/code-423n4/2022-05-rubicon/blob/8c312a63a91193c6a192a9aab44ff980fbfd7741/contracts/rubiconPools/BathHouse.sol#L171-L178)
