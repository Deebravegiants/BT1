# [M] Supply limitation misbehaviors

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In `SWSupplyManager` contract, the `owner` can limit supply for any token ID by setting `maxSupply`:


**code/contracts/shop/SWSupplyManager.sol:L149-L165**
```solidity
function setMaxSupplies(uint256[] calldata _ids, uint256[] calldata _newMaxSupplies) external onlyOwner() {
  require(_ids.length == _newMaxSupplies.length, "SWSupplyManager#setMaxSupply: INVALID_ARRAYS_LENGTH");

  // Can only *decrease* a max supply
  // Can't set max supply back to 0
  for (uint256 i = 0; i < _ids.length; i++ ) {
    if (maxSupply[_ids[i]] > 0) {
      require(
        0 < _newMaxSupplies[i] && _newMaxSupplies[i] < maxSupply[_ids[i]],
        "SWSupplyManager#setMaxSupply: INVALID_NEW_MAX_SUPPLY"
      );
    }
    maxSupply[_ids[i]] = _newMaxSupplies[i];
  }

  emit MaxSuppliesChanged(_ids, _newMaxSupplies);
}
```

The problem is that you can set `maxSupply` that is lower than `currentSupply`, which would be an unexpected state to have. 

Also, if some tokens are burned, their `currentSupply` is not decreasing:


**code/contracts/shop/SWSupplyManager.sol:L339-L345**
```solidity
function burn(
  uint256 _id,
  uint256 _amount)
  external
{
  _burn(msg.sender, _id, _amount);
}
```

This unexpected behaviour may lead to burning all of the tokens without being able to mint more.

#### Recommendation

Properly track `currentSupply` by modifying it in `burn` function. 
Consider having a following restriction `require(_newMaxSupplies[i] > currentSupply[_ids[i]])` in `setMaxSupplies` function.
