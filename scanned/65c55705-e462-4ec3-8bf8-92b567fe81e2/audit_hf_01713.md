# [M] M-8 Centralization risks

## Summary
Severity: Medium
Contest weight: 0.0548
Dataset id: 9345
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The project administrator and manager have unrestricted rights, including:
• Contract code updates,
• Project configuration changes,
• Addition of an arbitrary number of RSETH minters (though minting capability is only used in LRTDepositPool),
• Oracle appointments.
These permissions pose centralization risks.

## Recommendation
We recommend creating a DAO system with time-delayed execution of updates.
