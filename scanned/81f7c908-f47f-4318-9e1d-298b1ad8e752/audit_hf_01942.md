# [M] M-5 Centralization risks

## Summary
Severity: Medium
Contest weight: 0.1429
Dataset id: 10719
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LST Adapter contracts implement a centralized governance model with two privileged roles: owner and rebalancer. The owner has extensive control, including:  
• Modifying the tranche value of an adapter, potentially halting all previewDeposit and previewRedeem functions marked with the onlyTranche modiﬁer.  
• Pausing/unpausing staking, altering staking limits, and assigning a new rebalancer to the pool.  
The rebalancer role, while less powerful, can also signiﬁcantly impact user experience by:  
• Initiating withdrawal requests to integrated LST projects.  
• Adjusting the adapter's buffer percentage.  
If the rebalancer fails to initiate withdrawal requests, users will be unable to redeem their funds until the owner intervenes. This centralization of control introduces a single point of failure and poses a risk to user trust.

## Recommendation
We recommend implementing a mechanism to prevent the modiﬁcation of the tranche value while the tranche holds a non-zero balance of adapter shares. This ensures the intended functionality of the onlyTranche-marked functions. Additionally, we suggest considering a more distributed mechanism for withdrawing funds from integrated projects to mitigate the reliance on a single rebalancer for user redemptions.
