# [M] M-02 | Native Ether Can Not Be Deposited

## Summary
Severity: Medium
Contest weight: 0.0788
Dataset id: 2537
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The exec function of the Position contract can transfer native ether, as this might be needed to interact with some protocols (for example to pay gas for a 2-step flow).
But it is not possible to use this feature as ether can not be deposited into the Position contract:
• The deposit function can not be used to deposit native ether
• The exec function is not payable
• And there is no receive or fallback function in the Position contract

## Recommendation
Implement the possibility to deposit native ether and/or make the exec functions payable and forward the msg.value from the PositionManager to the Position contract.
