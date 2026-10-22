# [M] 0.3% of numeraire will be lost if protocol does not reach minimum minimumProceeds

## Summary
Severity: Medium
Reporter: deadrosesxyz
Contest weight: 0.5826
Dataset id: 4594
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the scenario where minimumProceeds is not reached after endingTime, the protocol takes the average buy price and adds all numeraire as liquidity on it so all buyers can withdraw their funds at a fair price.
```solidity
// Place all available numeraire in the lower slug at the average clearing price
BalanceDelta delta = _clearPositions(prevPositions, key);
uint256 numeraireAvailable = uint256(uint128(isToken0 ? delta.amount1() : delta.amount0()));
SlugData memory lowerSlug =
    _computeLowerSlugInsufficientProceeds(key, numeraireAvailable, state.totalTokensSold);
Position[] memory newPositions = new Position[](1);
newPositions[0] = Position({
    tickLower: lowerSlug.tickLower,
    tickUpper: lowerSlug.tickUpper,
    liquidity: lowerSlug.liquidity,
    salt: uint8(uint256(LOWER_SLUG_SALT))
});
```
The problem is that the protocol does not account for the pool fees. Currently, they're set to 0.3% (in test files their ovewritten to 0.03% for simplicity I believe). For this reason, when all users sell back their assets, 0.3% of the numeraire will actually remain stuck.

Impact Explanation:
As 0.3% is not negligible and will often be lost, I believe issue is Medium/High severity.

## Proof of Concept
```solidity
function testFeesGetStuck() public {
    vm.warp(hook.getStartingTime());
    buy(1e18);
    vm.warp(hook.getEndingTime());
    sell(-1e18);
    console.log("%e", TestERC20(numeraire).balanceOf(address(manager)));
    // all tokens are sold and there's still numeraire within the manager
}
```

## Recommendation
Account for the swap fees when calculating the price where liquidity is added. Or, alternatively, set the Univ4 pool to dynamic fee and upon not reaching quota, set the fee to 0.
