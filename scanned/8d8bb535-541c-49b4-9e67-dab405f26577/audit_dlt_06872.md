# [M] Wrong shareChange() function (vToken.sol)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-04-phuture
Published: 2022-04-21
Source: https://github.com/code-423n4/2022-04-phuture-findings/issues/26
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-04-phuture/blob/594459d0865fb6603ba388b53f3f01648f5bb6fb/contracts/vToken.sol#L160


# Vulnerability details

## Impact
Users can get the wrong amount of vToken 
=> Make users lose their fund 

## Proof of Concept
Base on the code in function ```shareChange()``` in [vToken.sol](https://github.com/code-423n4/2022-04-phuture/blob/main/contracts/vToken.sol)
Assume that if ```oldShare = totalSupply > 0```, 
* ```newShares``` 
= ```(_amountInAsset * (_totalSupply - oldShares)) / (_assetBalance - availableAssets);```
= ```(_amountInAsset * (_totalSupply - _totalSupply)) / (_assetBalance - availableAssets);```
= ```0```

It make no sense, because if ```amountInAsset >> availableAssets```, ```newShares``` should be bigger than ```oldShares```, but in this case ```newShares = 0 < oldShares```

## Tools Used
manual review 

## Recommended Mitigation Steps
Modify the [line](https://github.com/code-423n4/2022-04-phuture/blob/594459d0865fb6603ba388b53f3f01648f5bb6fb/contracts/vToken.sol#L160) from ```if (_totalSupply > 0)``` to ```if (_totalSupply - oldShares > 0)```
