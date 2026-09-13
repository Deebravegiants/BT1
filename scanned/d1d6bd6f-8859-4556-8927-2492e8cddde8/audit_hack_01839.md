# [H] Node can unlink validator

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Validators can link a node address to them by calling `linkNodeAddress` function:


**code/contracts/delegation/ValidatorService.sol:L109-L119**
```solidity
function linkNodeAddress(address validatorAddress, address nodeAddress) external allow("DelegationService") {
    uint validatorId = getValidatorId(validatorAddress);
    require(_validatorAddressToId[nodeAddress] == 0, "Validator cannot override node address");
    _validatorAddressToId[nodeAddress] = validatorId;
}

function unlinkNodeAddress(address validatorAddress, address nodeAddress) external allow("DelegationService") {
    uint validatorId = getValidatorId(validatorAddress);
    require(_validatorAddressToId[nodeAddress] == validatorId, "Validator hasn't permissions to unlink node");
    _validatorAddressToId[nodeAddress] = 0;
}
```

After that, the node has the same rights and is almost indistinguishable from the validator. So the node can even remove validator's address from `_validatorAddressToId` list and take over full control over validator. Additionally, the node can even remove itself by calling `unlinkNodeAddress`, leaving validator with no control at all forever. 

Also, even without nodes, a validator can initially call `unlinkNodeAddress` to remove itself.


#### Recommendation

Linked nodes (and validator) should not be able to unlink validator's address from the `_validatorAddressToId` mapping.
