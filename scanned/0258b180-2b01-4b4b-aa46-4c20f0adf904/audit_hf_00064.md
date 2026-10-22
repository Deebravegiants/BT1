# [M] M-03 | Bad Debt Value Extraction

## Summary
Severity: Medium
Contest weight: 0.1519
Dataset id: 140
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When positions with bad debt are liquidated on a tick where the liquidation price without penalty is above the current price, then a correction is made to the balance of the vault. The losses which are in excess of the position's collateral were errantly counted as going towards the vault. Upon liquidation these errant trader losses are clawed back from the vault. Depositors may observe that this correction is going to occur if a liquidation round occurs and intentionally frontrun this to initiate a withdrawal. The initiation of a withdrawal will protect the depositor from this clawing back of inaccurate trader losses because the balanceVault and balanceLong are cached on the withdrawal object. Furthermore this clawing back of bad debt can cause a stepwise decrease in the price of USDN which may also be arbitrageable by shorting USDN.

## Proof of Concept
https://github.com/GuardianAudits/usdn-1/pull/10/files#diff-f713a8103547db0e4f41b3ade28c2da19617b369df0d98bb416c80db690e5517R57

## Recommendation
Be aware of this risk of late liquidations and carefully consider it when configuring liquidation rewards and liquidation penalties.
