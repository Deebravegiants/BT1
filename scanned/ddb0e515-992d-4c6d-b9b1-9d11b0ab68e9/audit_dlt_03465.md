# [M] after unregisterSingularity() , position has not been unlock will be locked in the contract.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-02-tapioca
Published: 2024-03-18
Source: https://github.com/code-423n4/2024-02-tapioca-findings/issues/110
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token/blob/20a83b1d2d5577653610a6c3879dff9df4968345/contracts/options/TapiocaOptionLiquidityProvision.sol#L334


# Vulnerability details

## Vulnerability details

when `singularity.rescue==true`, owner can execute `unregisterSingularity()`
this method will delete `activeSingularities[]/sglAssetIDToAddress[]`
```solidity
    function unregisterSingularity(IERC20 singularity) external onlyOwner updateTotalSGLPoolWeights {
        uint256 sglAssetID = activeSingularities[singularity].sglAssetID;
        if (sglAssetID == 0) revert NotRegistered();
        if (!activeSingularities[singularity].rescue) revert NotInRescueMode();

        unchecked {
            uint256[] memory _singularities = singularities;
            uint256 sglLength = _singularities.length;
            uint256 sglLastIndex = sglLength - 1;

            for (uint256 i; i < sglLength; i++) {
                if (_singularities[i] == sglAssetID) {
                    // If in the middle, copy last element on deleted element, then pop
@>                  delete activeSingularities[singularity];
@>                  delete sglAssetIDToAddress[sglAssetID];

                    if (i != sglLastIndex) {
                        singularities[i] = _singularities[sglLastIndex];
                    }
                    singularities.pop();
                    emit UnregisterSingularity(address(singularity), sglAssetID);
                    break;
                }
            }
        }

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-tapioca-findings/issues/110_
