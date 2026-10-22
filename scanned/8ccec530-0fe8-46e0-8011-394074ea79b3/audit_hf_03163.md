# [H] _deleteLienPosition can be called by anyone

## Summary
Severity: High
Contest weight: 0.5809
Dataset id: 17722
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_deleteLienPosition is a public function that doesn't check the caller. This allows anyone to call it and remove whatever lien they wish from whatever collateral they wish
```solidity
function _deleteLienPosition(uint256 collateralId, uint256 position) public {
    uint256[] storage stack = liens[collateralId];
    require(position < stack.length, "index out of bounds");
    emit RemoveLien(
        stack[position],
        lienData[stack[position]].collateralId,
        lienData[stack[position]].position
    );
    for (uint256 i = position; i < stack.length - 1; i++) {
        stack[i] = stack[i + 1];
    }
    stack.pop();
}
```
_deleteLienPosition is a public function and doesn't validate that it's being called by any permissioned account. The result is that anyone can call it to delete any lien that they want. It wouldn't remove the lien data but it would remove it from the array associated with collateralId, which would allow it to pass the CollateralToken.sol#releaseCheck and the underlying to be withdrawn by the user. All liens can be deleted completely rugging lenders

## Recommendation
Change _deleteLienPosition to internal rather than public.
