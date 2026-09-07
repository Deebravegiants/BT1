# [M] `TapiocaOptionLiquidityProvision.registerSingularity()` not checking for duplicate assetIds leading to multiple issues.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1350
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L276-L293
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L315
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionLiquidityProvision.sol#L340
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L184
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L385
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L561-L570


# Vulnerability details

## Impact

When registering multiple singularities via `TapiocaOptionLiquidityProvision.registerSingularity()` it is possible to specify the same `assetID` for different singularities. This leads to a couple of issues, since for example after the 2nd singularity with the same `assetID` was registered, `sglAssetIDToAddress[assetID]` will point to the 2nd singularity as a result (line 289 TapiocaOptionLiquidityProvision.sol). Thus the following issues occur:

1. The `TapiocaOptionLiquidityProvision.totalSingularityPoolWeights` state variable will have a wrong value, since `TapiocaOptionLiquidityProvision._computeSGLPoolWeights()` adds `activeSingularities[sglAssetIDToAddress[singularities[i]]` to `total` (line 340 TapiocaOptionLiquidityProvision), where `sglAssetIDToAddress[singularities[i]]` translates into
`sglAssetIDToAddress[assetID]` which points to the 2nd singularity that was registered with the same `assetID`, ignoring the 1st singularity that was registered before with the same `assetID`. So the `TapiocaOptionLiquidityProvision.totalSingularityPoolWeights` will be off, which is used in the TapiocaOptionBroker line 561-571 to calculate the `quotaPerSingularity`.

1. `TapiocaOptionLiquidityProvision.getTotalPoolDeposited()` will also return a wrong value, since the method also uses `activeSingularities[sglAssetIDToAddress[_sglAssetId]]` which again points to the 2nd singularity that was registered with the same `assetID` and used the `totalDeposited` from the 2nd singularity, but doesn't take into account the `totalDeposited` from the first singularity that was registered with the same `assetID`. `TapiocaOptionLiquidityProvision.getTotalPoolDeposited()` is also used in the `TapiocaOptionBroker` on two places for calculating the `eligibleTapAmount` (line 184, 385 in TapiocaOptionBroker.sol)

1. The wrong pools array may be returned by `TapiocaOptionLiquidityProvision.getSingularityPools()`, where the 2nd singularity that was registered with the same `assetID` will be returned twice and the 1st singularity that was registered with the same `assetID` will not be included in the return value `pools` array, since the `pools` array is also assigned the value of `activeSingularities[sglAssetIDToAddress[_singularities[i]]` which always points to the 2nd singularity that was registered with the same `assetID`.

1. If you unregister a singularity with `TapiocaOptionLiquidityProvision.unregisterSingularity()` it may also remove the wrong singularity that has the same `assetID` (line 315 TapiocaOptionLiquidityProvision.sol).

## Proof of Concept

Here is a POC that shows that the `TapiocaOptionLiquidityProvision.totalSingularityPoolWeights` is off when multiple singularities are registered with the same `assetID`:

https://gist.github.com/zzzitron/19ab8bc5853176f3521af99d0e4ba0fc

## Tools Used

Manual review

## Recommended Mitigation Steps

Consider not allowing to register multiple singularities with the same `assetID`:

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1350_
