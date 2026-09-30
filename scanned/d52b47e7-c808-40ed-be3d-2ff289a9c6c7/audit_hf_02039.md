# [M] Proper Interest Attribution in Vault::accrue()

## Summary
Severity: Medium
Contest weight: 0.4095
Dataset id: 11624
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the same vein as the utilization rate computation in Section 3.5, the Vault in the Amy protocol allows for the accrual of interests from the borrowed assets for leverage. And a portion of the accrued interest will be reserved for protocol development, insurance fund, or team incentivization purposes. However, our analysis shows that there is not fund reserved for this purpose.  
To elaborate, we show below the accrue() routine from the Vault contract. This routine calls an internal helper function pendingInterest() to collect pending interest form the borrowed funds and records the latest accrual timestamp in lastAccrueTime. To properly allocate certain portion of collected interests, there is a need to expand the current functionality for reserve purposes.
```solidity
/// Add more debt to the bank debt pool.
modifier accrue(uint256 value) {
    if (now > lastAccrueTime) {
        uint256 interest = pendingInterest(value);
        vaultDebtVal = vaultDebtVal.add(interest);
        lastAccrueTime = now;
    }
    _;
}
```

## Recommendation
Support the reserve funds by revising the above logic in accrue().
