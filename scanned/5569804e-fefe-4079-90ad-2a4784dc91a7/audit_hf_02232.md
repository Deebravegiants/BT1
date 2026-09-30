# [M] Incorrect vestingStartTime Activation in harvestPool()

## Summary
Severity: Medium
Contest weight: 0.4332
Dataset id: 12316
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The token sale contract is designed with a global state vestingStartTime, which marks the vesting start time for everyone. However, this global start time needs to coordinate with all remaining pools as there is a need to ensure all pools have passed their end times. To elaborate, we show below the related harvestPool() routine that initializes the vesting start time when the first user successfully claims the offering token. (Due to the vesting schedule, the claimed amount is only a portion of entire vesting amount.) However, it does not check whether all other pools have completed the sale. If there is a pool with uncompleted sale, the vesting for all users should not be started. To mitigate, we may have a pool-specific vesting start time to avoid the need to coordinate with other pools.
```solidity
function harvestPool(uint8 _pid) external nonReentrant notContract {
    require(harvestAllowed, "Harvest: Not allowed");
    // Checks whether it is too early to harvest
    require(block.timestamp > _poolInformation[_pid].endTime, "Harvest: Too early");
    // Checks whether pool id is valid
    require(_pid < NUMBER_POOLS, "Harvest: Non valid pool id");
    // Checks whether the user has participated
    require(_userInfo[msg.sender][_pid].amountPool > 0, "Harvest: Did not participate");
    // Checks whether the user has already harvested
    require(!_userInfo[msg.sender][_pid].claimedPool, "Harvest: Already done");
    // Updates the harvest
}
```

## Recommendation
Ensure all pools have completed the sale if the vesting start time is initialized.
