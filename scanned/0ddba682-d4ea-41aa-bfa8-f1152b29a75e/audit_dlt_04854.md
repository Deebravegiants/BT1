# [M] `NFTCollection.sol`: Initial Royalties can be over 100%

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/102
Type: sherlock-finding

## Details
Dravee

medium

# `NFTCollection.sol`: Initial Royalties can be over 100%

## Summary
Initial Royalties can be over 100% (over `ROYALTIES_BASIS = 10000`)

## Vulnerability Detail
While there's a call to `_validateRuntimeConfig` which checks that royalties are below a certain bound in the event of an update (`updateConfig`), this is not the case in the `initialize` function.

## Impact
Royalties over 100%

## Code Snippet
`initialize` function which calls `_validateDeploymentConfig` but not `_validateRuntimeConfig`:

https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L141-L156

`updateConfig` which indeed calls `_validateRuntimeConfig`:

https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L289-L295

Upper bound check for royalties in `_validateRuntimeConfig`:

https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/NFTCollection.sol#L343-L348

## Tool used

Manual Review

## Recommendation
Add a call to `_validateRuntimeConfig` in `initialize`

Duplicate of #83
