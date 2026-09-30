# [M] Lack of resumePresale function leads to incorrect fundraisingEndTime adjustment

## Summary
Severity: Medium
Contest weight: 0.4084
Dataset id: 8755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The HolofairToken contract includes a pausePresale function that allows the creator to pause the presale. However, the only way to resume the presale after it has been paused is by calling the startPresale function. This approach inadvertently resets the fundraisingEndTime by adding the fundraisingPeriod to the current block timestamp, effectively extending the presale duration. This extension can disrupt the vesting schedule for users who have already deposited funds, as their vesting unlock time is tied to the original fundraisingEndTime.
```solidity
function startPresale() external {
    require(msg.sender == creator, "Only creator can start presale");
    require(!presaleActive, "Presale already started");
    fundraisingEndTime = block.timestamp + fundraisingPeriod;
    presaleActive = true;
}
function pausePresale() external {
    require(msg.sender == creator, "Only creator can pause presale");
    require(presaleActive, "Presale already paused");
    presaleActive = false;
}
```

## Recommendation
Implement a resumePresale function that allows the presale to be resumed without modifying the fundraisingEndTime.
