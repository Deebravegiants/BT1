# [M] UsersCanPreventMaximumDepositCapfromBeingReached

## Summary
Severity: Medium
Contest weight: 0.4643
Dataset id: 8645
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability arises in the depositEth() function within the contract, specifically when dealing with the launchParams.maxRaiseAmount and launchParams.minAllocation parameters. The contract imposes a minimum allocation requirement for deposits, ensuring that each deposit is at least a certain amount (minAllocation) and that the total amount raised does not exceed the maximum cap (maxRaiseAmount). However, a logical flaw exists in the way the contract handles situations where the total raised amount (totalRaised) is close to the maximum raise amount (maxRaiseAmount), but the remaining capacity for deposits is less than the minimum deposit amount (minAllocation). In this case, users cannot deposit any amount that is lower than the minAllocation, even if the remaining capacity is sufficient to accept smaller deposits. This prevents the contract from fully reaching its maximum raise amount and effectively “locks” the remaining space, causing it to remain unused. For example, if launchParams.maxRaiseAmount is set to 100 and launchParams.minAllocation is set to 10, and the current totalRaised is 95, any deposit attempt below 10 (e.g., a deposit of 5) would be rejected, even though the remaining capacity is exactly 5. As a result, the contract would never reach its maximum raise amount of 100, even though there is still available capacity for a smaller deposit.

This vulnerability has the potential to lead to a denial of service (DoS) situation, where the remaining deposit capacity cannot be used effectively. As a result, the contract will not reach its intended fundraising goal.

## Recommendation
To resolve this issue, the depositEth() function should be modified to allow deposits that are smaller than the minAllocation when the remaining capacity in the contract is less than the minAllocation.

```solidity
function depositEth()
    external
    payable
    atPhase(LEAPDataTypes.Phase.PHASE_DEPOSIT)
    nonReentrant
{
    uint256 _value = msg.value;
    // if the whitelist is enabled and the user is not whitelisted, revert
    if (launchParams.isWhitelistEnabled && !whitelist[msg.sender])
        revert Errors.ERR_WhitelistRequired(msg.sender);
    // uncapped if set to 0 initially
    if (launchParams.maxRaiseAmount != 0) {
        if (totalRaised + _value > launchParams.maxRaiseAmount)
            revert Errors.ERR_MaximumDepositReached();
    }
    // Perform required checks to make sure deposit is valid
    if (_value == 0) revert Errors.ERR_NoEthDeposited();
    if (_value < launchParams.minAllocation) {
        uint256 remainingCapacity = launchParams.maxRaiseAmount - totalRaised;
        // Allow deposits that are smaller than minAllocation if they fit in the remaining capacity
        if (_value < launchParams.minAllocation && _value != remainingCapacity) {
            revert Errors.ERR_RequiresMinimumAmount();
        }
    }
}
```
