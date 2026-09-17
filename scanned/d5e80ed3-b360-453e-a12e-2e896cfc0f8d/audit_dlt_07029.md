# [M] M-05 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-06-xeth-mitigation
Published: 2023-06-16
Source: https://github.com/code-423n4/2023-06-xeth-mitigation-findings/issues/13
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-xeth/blob/add-xeth/src/wxETH.sol#L230


# Vulnerability details

The mitigation makes accrueDrip is disable until the `totalSupply() > 0`. But the `lastReport` blocknumber is not updated. So all the dripped rewards still are collected by the first staker when the `drip` modifier is called at the second time.

## Impact
If wxETH drips when nothing is staked, then the first staker can claim every drop.

## Proof of Concept
After patch with the mitigation, the first call to `stake` function will skip the `_accrueDrip` modifier because of `totalSupply() == 0`. So the `lastReport` blocknumber is not updated. 

And the `exchangeRate` in the `previewStake` function returns `INITIAL_EXCHANGE_RATE` because of:
```
    function exchangeRate() public view returns (uint256) {
        if (_totalSupply == 0) {
            return INITIAL_EXCHANGE_RATE;
        }
```
So the mint amount is not changed after the mitigation for the first staker. 

When some one calls the `drip` modifier at the second time, such as `unstake` from the first staker or `stake` from someone else, the `drip` modifier will accrue the `dripAmount` from `block.number - lastReport`, which begined since `startDrip` instead of the first `stake`.

So the first staker still can get all of them.

## Tools Used
Manual review
## Recommended Mitigation Steps
Only update the `lastReport` when totalSupply is zero.
```
if(totalSupply() == 0){
    lastReport = block.number;
    return;
}
```


## Assessed type

MEV
