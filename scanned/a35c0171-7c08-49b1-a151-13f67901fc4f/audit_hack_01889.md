# [M] Missing Input Validation

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

* There is no zero address check in function `addOperator` for the operator address and fee recipient. Also, the function doesn't check whether the operator already exists.


**src/contracts/StakingContract.sol:L392-L405**
```solidity
function addOperator(address _operatorAddress, address _feeRecipientAddress) external onlyAdmin returns (uint256) {
    StakingContractStorageLib.OperatorsSlot storage operators = StakingContractStorageLib.getOperators();
    StakingContractStorageLib.OperatorInfo memory newOperator;

    if (operators.value.length == 1) {
        revert MaximumOperatorCountAlreadyReached();
    }
    newOperator.operator = _operatorAddress;
    newOperator.feeRecipient = _feeRecipientAddress;
    operators.value.push(newOperator);
    uint256 operatorIndex = operators.value.length - 1;
    emit NewOperator(_operatorAddress, _feeRecipientAddress, operatorIndex);
    return operatorIndex;
}
```

* No zero address check in function `setTreasury` for updating the treasury address.

**src/contracts/StakingContract.sol:L214-L217**
```solidity
function setTreasury(address _newTreasury) external onlyAdmin {
    emit ChangedTreasury(_newTreasury);
    StakingContractStorageLib.setTreasury(_newTreasury);
}
```

* Functions `activateOperator` and `deactivateOperator` as the name hints, allow the admin to activate or deactivate an operator. However, the functions don't check for already activated/deactivated operators, and may still emit `DeactivatedOperator`/`ActivatedOperator` events for an operator. It may trigger false alarms for off-chain monitoring tools and create unnecessary panic.

**src/contracts/StakingContract.sol:L479-L502**
```solidity
/// @notice Deactivates an operator and changes the fee recipient address and the staking limit
/// @param _operatorIndex Operator Index
/// @param _temporaryFeeRecipient Temporary address to receive funds decided by the system admin
function deactivateOperator(uint256 _operatorIndex, address _temporaryFeeRecipient) external onlyAdmin {
    StakingContractStorageLib.OperatorsSlot storage operators = StakingContractStorageLib.getOperators();
    operators.value[_operatorIndex].limit = 0;
    emit ChangedOperatorLimit(_operatorIndex, 0);
    operators.value[_operatorIndex].deactivated = true;
    emit DeactivatedOperator(_operatorIndex);
    operators.value[_operatorIndex].feeRecipient = _temporaryFeeRecipient;
    emit ChangedOperatorAddresses(_operatorIndex, operators.value[_operatorIndex].operator, _temporaryFeeRecipient);
    _updateAvailableValidatorCount(_operatorIndex);
}

/// @notice Activates an operator, without changing its 0 staking limit
/// @param _operatorIndex Operator Index
/// @param _newFeeRecipient Sets the fee recipient address
function activateOperator(uint256 _operatorIndex, address _newFeeRecipient) external onlyAdmin {
    StakingContractStorageLib.OperatorsSlot storage operators = StakingContractStorageLib.getOperators();
    operators.value[_operatorIndex].deactivated = false;
    emit ActivatedOperator(_operatorIndex);
    operators.value[_operatorIndex].feeRecipient = _newFeeRecipient;
    emit ChangedOperatorAddresses(_operatorIndex, operators.value[_operatorIndex].operator, _newFeeRecipient);
}
```
