# [M] Incorrect computeVestingScheduleIdForAddressAndPid() Logic

## Summary
Severity: Medium
Contest weight: 0.4262
Dataset id: 12310
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the audited token sale contract, there is a helper routine computeVestingScheduleIdForAddressAndPid() that is designed to compute the vesting schedule identifier for a given address and a sale pool. Our analysis indicates that the generated identifier assumes the given address has no more than 2 vesting schedules, which can be relaxed. In the following, we show the implementation of this specific routine. It has two arguments _holder and _pid. The logic is implemented to try the first possible identifier for the given _holder. If the pool id matches, we have successfully located the requested vesting schedule. Otherwise, it simply computes the next possible vesting schedule identifier. This computation may not be correct if the given _holder has more than 2 vesting schedules.
```solidity
function computeVestingScheduleIdForAddressAndPid(address _holder, uint256 _pid) external view returns (bytes32) {
    require(_pid < NUMBER_POOLS, "ComputeVestingScheduleId: Non valid pool id");
    bytes32 vestingScheduleId = computeVestingScheduleIdForAddressAndIndex(_holder, 0);
    VestingSchedule memory vestingSchedule = vestingSchedules[vestingScheduleId];
    if (vestingSchedule.pid == _pid) {
        return vestingScheduleId;
    } else {
        return computeVestingScheduleIdForAddressAndIndex(_holder, 1);
    }
}
```

## Recommendation
Revise the above routine to accommodate the possibility of having multiple vesting schedules.
