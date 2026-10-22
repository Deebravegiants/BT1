# [M] M-02 | Liquidations Prevented By Frontrunning

## Summary
Severity: Medium
Contest weight: 0.1042
Dataset id: 2567
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If an account is liquidatable on V2X, it is expected to be forcibly migrated to the V3 system where it will be liquidated. It cannot be liquidated on V2X. However, migrateOnBehalf can be DOS-ed by front-running the liquidator and creating an account in the V3 system with the requested accountId. Then the migrateOnBehalf call would fail and revert since an identical accountId already exists. Apart from gas costs, there is no limitation to how many times an account can be created to perform this DOS attack and avoid liquidation, which could result in bad debt to the system.

## Recommendation
Re-consider allowing users to pass in requestedAccountId in createAccount in the V3 system and instead use the createAccount() function which automatically assigns the next free account number. Otherwise be sure to document that liquidations should use MEV protection such as flash-bots.
