# [M] After `unregisterSingularity

## Summary
Severity: Medium
Contest weight: 0.6924
Dataset id: 20791
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
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
                delete activeSingularities[singularity];
                delete sglAssetIDToAddress[sglAssetID];

                if (i != sglLastIndex) {
                    singularities[i] = _singularities[sglLastIndex];
                }
                singularities.pop();
                emit UnregisterSingularity(address(singularity), sglAssetID);
                break;
            }
        }
    }

    emit UnregisterSingularity(address(singularity), sglAssetID);
}
```
However, this method does not determine whether there are still has locked positions. In this way, if the user wants to `unlock()`, it will not be executed and the `token` will be locked in the contract.

`activeSingularities[_singularity]` has been deleted.
```solidity
function unlock(uint256 _tokenId, IERC20 _singularity, address _to) external {
    ...
    SingularityPool memory sgl = activeSingularities[_singularity];

    yieldBox.transfer(address(this), _to, lockPosition.sglAssetID, lockPosition.ybShares);
    activeSingularities[_singularity].totalDeposited -= lockPosition.ybShares;

    emit Burn(_to, lockPosition.sglAssetID, _tokenId);
}
```

## Recommendation
```solidity
function unregisterSingularity(IERC20 singularity) external onlyOwner updateTotalSGLPoolWeights {
    ...
    for (uint256 i; i < sglLength; i++) {
        if (_singularities[i] == sglAssetID) {
            //check totalDeposited
            require(activeSingularities[singularity].totalDeposited == 0 , "invalid");

            // If in the middle, copy last element on deleted element, then pop
            delete activeSingularities[singularity];
            delete sglAssetIDToAddress[sglAssetID];

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
