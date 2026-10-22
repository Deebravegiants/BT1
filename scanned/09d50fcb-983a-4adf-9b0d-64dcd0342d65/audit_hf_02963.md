# [M] claim method should be usable while the WhirlVesting contract is paused

## Summary
Severity: Medium
Contest weight: 0.3908
Dataset id: 16417
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The WhirlVesting:claim function is only callable when the WhirlVesting contract is not paused. This prevents a user from collecting accumulated funds. The admin of the WhirlVesting contract can potentially pause the contracts at any time, locking users out of their honestly earned funds.
```solidity
function claim() external {
    _checkPaused();
    Vesting storage vesting = vestings[msg.sender];
    uint256 claimable = _claimable(vesting.total, vesting.claimed);
    if (claimable == 0) _revert(NothingToClaim.selector);
    unchecked {
        vesting.claimed += claimable;
        _safeTransfer(token, msg.sender, claimable);
        emit Claimed(msg.sender, claimable);
    }
}
```

## Recommendation
Consider removing the _checkPaused from the claim function to allow claiming while the WhirlVesting contract is paused.
