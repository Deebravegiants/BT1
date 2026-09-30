# [M] Revised Collateral Priority Update in setCollateralPriority()

## Summary
Severity: Medium
Contest weight: 0.4622
Dataset id: 12006
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ERD protocol, the CollateralManager contract maintains a list of the supported collaterals and their parameters. The collaterals are sorted in descending order per their priorities. The protocol owner has the right to add/remove collaterals and update their parameters. While examining the collateral priority update functionality, we notice a logical issue that may mess up the collaterals priority order and their parameters. To elaborate, we show below the code snippet of the setCollateralPriority() routine. As the name indicates, it is used to update the priority of the input collateral. Specically, if the new priority gets higher, the collateral is moved up from current index in the sorted collateral list. Similarly, when the new priority is lowered, the collateral is moved down from current index.
```solidity
function setCollateralPriority(
    address _collateral,
    uint256 _newIndex
) external override onlyOwner {
    _requireCollIsActive(_collateral);
    uint256 oldIndex = getIndex(_collateral);
    uint256 newIndex = _newIndex;
    assert(newIndex != oldIndex && newIndex < collateralsCount);
    if (newIndex < oldIndex) {
        uint256 tmpIndex = oldIndex;
        uint256 gap = oldIndex - newIndex;
        for (uint256 i = 0; i < gap; ) {
            tmpIndex = _up(tmpIndex);
            unchecked {
                i++;
            }
        }
    } else {
        uint256 tmpIndex = newIndex;
        uint256 gap = oldIndex - newIndex;
        for (uint256 i = 0; i < gap; ) {
            tmpIndex = _down(tmpIndex);
            unchecked {
                i++;
            }
        }
    }
    collateralParams[_collateral].index = _newIndex;
}
```
However, it comes to our attention that, when the priority gets lower, i.e., new index is larger than the old index, it tries to move the collateral at the new index while not the given collateral at the old index (line 177). Our analysis shows that the tmpIndex shall be set to oldIndex, i.e., uint256 tmpIndex = newIndex. What's more, it may revert the function because of arithmetic underflow when calculating the gap between the old index and the new index (line 178), i.e., uint256 gap = oldIndex - newIndex, because oldIndex <= newIndex in this case. In addition, during the process of moving the target collateral to the new index, the indexes of the collaterals on the moving path are also updated. However, it only links the collateralParams[_collateral] to the new index for the target collateral. As a result, the links in the collateralParams[_collateral] may be out-of-date for all the other affected collaterals. Based on this, we suggest to update the collateralParams[_collateral].index for all the collaterals whose indexes are updated.

## Recommendation
Revisit the collateral priority update in the setCollateralPriority() routine and properly update the positions of all the affected collaterals and update their collateralParams[_collateral].index accordingly.
