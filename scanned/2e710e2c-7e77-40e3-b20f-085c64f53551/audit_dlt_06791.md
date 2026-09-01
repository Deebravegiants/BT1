# [M] Collateral removal not possible

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-03-polynomial
Published: 2023-03-15
Source: https://github.com/code-423n4/2023-03-polynomial-findings/issues/16
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-03-polynomial/blob/main/src/ShortCollateral.sol#L262


# Vulnerability details

## Impact
If an approved collateral has later started say taking fees on transfer then protocol has no way to remove such collateral. The current deposit logic cannot handle fee on transfer token and would give more funds to user then actually obtained by contract

## Proof of Concept
1. Assume protocol was supporting collateral X (say USDT which has fee currently set as 0)
2. After some time collateral introduces fee on transfer
3. Protocol does not have a way to remove a whitelisted collateral
4. Problem begins once user starts depositing such collateral

```
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

5. In this case `amount` is transferred from user to contract but contract will only receive `amount-fees`. But contract will still adjust position with full `amount` instead of `amount-fees` which is incorrect

## Recommended Mitigation Steps
Add a way to disapprove collateral so that if in future some policy changes for a particular collateral, protocol can stop supporting it. This will it would only have to deal with existing collateral which can be wiped out slowly using public announcement
