# [M] Improved Logic of Pool::_addReserveToList()

## Summary
Severity: Medium
Contest weight: 0.4264
Dataset id: 11574
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Aave protocol allows the governance to dynamically add new reserves into the protocol. To keep track of the list of active reserves, the protocol maintains the internal state _reservesList. While reviewing the accounting of active reserves, we notice the internal routine to add a new reserve needs to be improved.
To elaborate, we show below the _addReserveToList() function. It implements a rather straightforward logic in validating the new asset and then adding it into the internal _reservesList. It comes to our attention that the internal for-loop needs to terminate the execution once a vacant spot is located and populated. Note the current implementation will simply fill all available slots with the new reserve asset.
```solidity
function _addReserveToList(address asset) internal {
    uint256 reservesCount = _reservesCount;
    require(reservesCount < _maxNumberOfReserves, Errors.P_NO_MORE_RESERVES_ALLOWED);
    bool reserveAlreadyAdded = (_reserves[asset].id != 0 || _reservesList[0] == asset);
    if (!reserveAlreadyAdded) {
        for (uint8 i = 0; i <= reservesCount; i++) {
            if (_reservesList[i] == address(0)) {
                _reserves[asset].id = i;
                _reservesList[i] = asset;
                _reservesCount = reservesCount + 1;
                break;
            }
        }
    }
}
```

## Recommendation
Revise the above _addReserveToList() function to properly add a new reserve asset.
