# [M] The Hats contract needs to override the ERC1155.balan

## Summary
Severity: Medium
Contest weight: 0.5726
Dataset id: 19756
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Hats contract does not override the ERC1155.balanceOfBatch function.
The Hats contract overrides the ERC1155.balanceOf function to return a balance of 0 when the hat is inactive or the wearer is ineligible.
```solidity
function balanceOf(address _wearer, uint256 _hatId)
    public
    view
    override(ERC1155, IHats)
    returns (uint256 balance)
{
    Hat storage hat = _hats[_hatId];
    balance = 0;
    if (_isActive(hat, _hatId) && _isEligible(_wearer, hat, _hatId)) {
        balance = super.balanceOf(_wearer, _hatId);
    }
}
```
But the Hats contract does not override the ERC1155.balanceOfBatch function, which causes balanceOfBatch to return the actual balance no matter what the circumstances.
```solidity
function balanceOfBatch(address[] calldata owners, uint256[] calldata ids)
    public
    view
    virtual
    returns (uint256[] memory balances)
{
    require(owners.length == ids.length, "LENGTH_MISMATCH");
    balances = new uint256[](owners.length);
    // Unchecked because the only math done is incrementing
    // the array index counter which cannot possibly overflow.
    unchecked {
        for (uint256 i = 0; i < owners.length; ++i) {
            balances[i] = _balanceOf[owners[i]][ids[i]];
        }
    }
}
```
This will make balanceOfBatch return a different result than balanceOf, which may cause errors when integrating with other projects.

## Recommendation
Consider overriding the ERC1155.balanceOfBatch function in Hats contract to return 0 when the hat is inactive or the wearer is ineligible.
