# [M] Collateral removal not possible

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 18313
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an approved collateral has later started say taking fees on transfer then protocol has no way to remove such collateral. The current deposit logic cannot handle fee on transfer token and would give more funds to user then actually obtained by contract

## Proof of Concept
1. Assume protocol was supporting collateral X (say USDT which has fee currently set as 0)
2. After some time collateral introduces fee on transfer
3. Protocol does not have a way to remove a whitelisted collateral
4. Problem begins once user starts depositing such collateral

```solidity
function _addCollateral(uint256 positionId, uint256 amount) internal {
    ...
    ERC20(shortPosition.collateral).safeTransferFrom(msg.sender, address(this), amount);
    ERC20(shortPosition.collateral).safeApprove(address(shortCollateral), amount);

    shortToken.adjustPosition(
        positionId,
        msg.sender,
        shortPosition.collateral,
        shortPosition.shortAmount,
        shortPosition.collateralAmount + amount
    );
    shortCollateral.collectCollateral(shortPosition.collateral, positionId, amount);
    ...
}
```

5. In this case `amount` is transferred from user to contract but contract will only receive `amount-fees`. But contract will still adjust position with full `amount` instead of `amount-fees` which is incorrect.

## Recommendation
Add a way to disapprove collateral so that if in future some policy changes for a particular collateral, protocol can stop supporting it. This will it would only have to deal with existing collateral which can be wiped out slowly using public announcement.

Not a duplicate of <https://github.com/code-423n4/2023-03-polynomial-findings/issues/178> as Fee-on-transfer tokens are only mentioned as a scenario that may make the protocol want to disapprove a collateral.

Due to a real lack of way to disapprove a collateral, I believe this finding is valid.
